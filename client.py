import argparse
import logging
import queue
import time
from socket import *
from datetime import datetime
import json
from threading import Thread

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys
import log.client_log_config
from client_app import MainClientWindow
from log.log_decorator import log
from dis import get_instructions

from server import on_clicked
from store import StoreClient


client_log = logging.getLogger('client')


class ClientVerifier(type):
    def __init__(cls, classname, bases, dict):

        for func in dict:
            try:
                instructions = get_instructions(dict[func])
            except TypeError:
                pass
            else:
                for op in instructions:
                    if op.opname == 'LOAD_GLOBAL':
                        if op.argval in ('accept', 'listen', 'socket'):
                            raise TypeError(f'{op.argval} cant use in class Client')
                    if op.opname == 'LOAD_METHOD':
                        if op.argval == 'create_socket_client':
                            raise TypeError(f'По ТЗ должно быть отсутствие создания сокетов на уровне классов')

        super().__init__(classname, bases, dict)


class Client(metaclass=ClientVerifier):
    def __init__(self, s, user, status):
        self.messages_list = []
        self.s = s
        self.user = user
        self.status = status
        self.db = None
        self.main_window = None
        self.online = []
        self.timer = QTimer()
        self.chat_arr = []
        self.q = queue.Queue()

    def run(self):
        """
        Основной метод класса с логикой чата
        :return:
        """
        print(f'client {self.user} starting...')
        client_log.info(f'client {self.user} starting...')
        self.db = StoreClient(self.user)
        print(f'{self.user} data base init...')
        client_log.info(f'{self.user} data base init...')
        presence_msg = self.presence(self.user, self.status)  # создаем presence-сообщение
        client_log.info('Presence message sending...')
        self.send_data(presence_msg, self.s)
        client_log.info('Presence message sending...DONE')

        client_app = QApplication(sys.argv)
        self.main_window = MainClientWindow(self.user)

        self.timer.timeout.connect(lambda: self.refresh_table())
        self.timer.start(2000)

        self.main_window.get_online.triggered.connect(lambda _: self.get_online(self.user, self.s))  # обновить онлайн
        self.main_window.get_online.triggered.connect(lambda _: self.main_window.write_online(db=self.db, online=self.online, chat_arr=self.chat_arr))
        self.main_window.all_clients.triggered.connect(lambda _: self.main_window.contact_list(db=self.db, online=self.online, chat_arr=self.chat_arr))  # клиенты-онлайн
        self.main_window.history.triggered.connect(lambda _: self.main_window.history_table(db=self.db, online=self.online, chat_arr=self.chat_arr))  # история сообщений
        self.main_window.valueChanged.connect(lambda: self.add_contact(
            user=self.user, s=self.s, contact=self.main_window.return_new_contact()))
        self.main_window.valueDelChanged.connect(
            lambda: self.del_contact(user=self.user, s=self.s, contact=self.main_window.return_new_contact()))

        self.main_window.chat_table.triggered.connect(lambda _: self.main_window.write_chat(db=self.db, online=self.online, chat_arr=self.chat_arr))

        self.main_window.sendChanged.connect(lambda _: self.main_send_message(message=self.main_window.show_message(), user=self.user, s=self.s))

        self.main_window.sendOne.connect(lambda _: self.main_send_message(message=self.main_window.show_message_to_one(), user=self.user, s=self.s))

        self.main_window.statusBar().showMessage('Lets go!')  # статус-бар

        try:
            data = self.data_from_server(self.s)
            answer = self.read_answer(data)
            print(f'Message(answer) from server received: ', answer)
        except:
            client_log.error('No messages from server.')
            exit(1)

        w = Thread(target=self.chat_w_message, args=(self.user, self.s))
        w.daemon = True
        w.start()

        r = Thread(target=self.chat_r_message, args=(self.s,))
        r.daemon = True
        r.start()

        client_app.exec_()
        while True:
            time.sleep(1)
            if not w.is_alive() or not r.is_alive():
                break

    @staticmethod
    def data_from_server(sock):
        """ функция(метод) для преобразования ответа с сервера в словарь
        :params: sock: socket
        :return: dict
        """
        received_data = sock.recv(10000000)
        decoded_data = received_data.decode('utf-8')
        result_data = json.loads(decoded_data)
        if type(result_data) == dict:
            return result_data
        return {}

    def read_answer(self, dict_from_server):
        """ функция(метод) для считывания ответа из данных (словаря), поступивших с сервера
        :params: dict
        :return str: >>>{username}: {text}
        """
        try:
            response_code = dict_from_server.get('response', 0)
        except Exception as err:
            client_log.error(f'Error {err})')
        else:
            if response_code:
                if response_code == 200:  # проверяем код
                    result_msg = dict_from_server.get('alert', 'OK.')
                    client_log.info('Response status OK')
                    try:
                        result_msg = dict_from_server.get('text', 0)  # пробуем достать текст сообщения
                    except Exception as err:
                        client_log.error(f'Error {err})')
                    else:
                        if result_msg:
                            return f'>>>{result_msg[1]}: {result_msg[0]}'  # если есть текст выводим сообщение и автора

                    return f'{response_code}: {result_msg}'

                if response_code == 202:
                    try:
                        result_msg = dict_from_server.get('alert')  # пробуем достать сообщение
                    except Exception as err:
                        client_log.error(f'Error {err})')
                    else:
                        if result_msg:
                            self.online = result_msg  # записываем всех клиентов, полученных с сервера в список
                            return f'>>>{result_msg}'

            client_log.error(f'Data : {dict_from_server}')

        return ''

    def chat_r_message(self, sock):
        """ функция(метод) отображения сообщений других пользователей, для работы в режиме "многопоточности".
        Пока клиент запущен будем ожидать сообщений от других клиентов
        :params: sock: socket
        """
        while True:
            try:
                data = self.data_from_server(sock)
                answer = self.read_answer(data)
                print(answer)
                self.chat_arr.append(answer)
                client_log.info(f'Message received: {answer} ')
            except Exception as err:
                client_log.error(f'Some errors in chat_r_message: {err}')
                exit(1)

    def chat_w_message(self, user, s):
        """ функция(метод) отправки сообщений другим пользователям, для работы в режиме "многопоточности".
        Пока клиент запущен будем ожидать ввода сообщения от пользователя
        :params: sock: socket
        """
        while True:
            message = input(f'>>>{user}\n')
            if message == 'exit':
                exit(0)

            if message == 'list':
                try:
                    print('Your contacts list: - ', self.db.get_contacts())
                except Exception as err:
                    client_log.error(f'Some errors in chat_w_message(list): {err}')

            if message == 'history':
                try:
                    print('Your history messages: - ', self.db.get_history())
                except Exception as err:
                    client_log.error(f'Some errors in chat_w_message(history): {err}')

            if message == 'online':  # клиент запрашивает получение списка контактов
                self.get_online(user, s)

            # Lesson 12 - Добавление/удаление контакта в список контактов
            if message == 'add':
                contact = input(f'>>>{user}: Write nickname new contact\n')
                self.add_contact(user, contact, s)

            if message == 'del':
                contact = input(f'>>>{user}: Write nickname to delete contact\n')
                self.del_contact(user, s, contact)

            else:
                # команды клиента, игнорируемые для отправки текстом
                commands_ignore = ['online', 'del', 'add', 'exit', 'list', 'history']
                if message not in commands_ignore:
                    self.main_send_message(message=message, user=user, s=s)
                pass

    @staticmethod
    def presence(account_name, status):
        """ функция(метод) для формирования presence-сообщения
        :params: account_name, status
        :return: dict
        """
        data = {
            "action": "presence",
            "time": datetime.timestamp(datetime.now()),
            "type": "status",
            "user": {
                "account_name": account_name,
                "status": status
            }
        }
        return data

    @staticmethod
    def send_data(data, sock):
        """функция(метод) отправки данных
        :param sock: socket
        :param data: dict
        """
        result_data = json.dumps(data).encode('utf-8')
        sock.send(result_data)

    @staticmethod
    def message_to_server(message, account_name):
        """ функция(метод) для формирования сообщения
        :params: message: text, account_name
        :return: dict
        """
        data = {
            "action": "message",
            "time": datetime.timestamp(datetime.now()),
            "text": message,
            "user": {
                "account_name": account_name,
            }
        }
        return data

    # GUI and other Functions
    def refresh_table(self):
        self.main_window.table(db=self.db, online=self.online, chat_arr=self.chat_arr)

    def main_send_message(self, message, user, s):
        self.messages_list.append(message)
        if self.messages_list != []:
            try:  # стандартный протокол отправки сообщения на сервер
                self.send_data(self.message_to_server(message, user), s)
                receivers = self.get_receivers()
                print('receivers', receivers)
                for client in receivers:
                    if type(message) is list:
                        self.db.add_history(client, message[0])
                    else:
                        self.db.add_history(client, message)
                self.chat_arr.append(f'>>>YOU({user}): {message}')
                del self.messages_list[-1]
            except Exception as err:
                client_log.error(f'Some errors in main part chat_w_message: {err}')

    # def to_one_message(self, message, user, s, contact):
    #     try:  # протокол отправки сообщения на сервер для одного клиента (вызов через приложение)
    #         message = [message, contact]
    #         self.send_data(self.message_to_server(message, user), s)
    #         receivers = self.get_receivers()
    #         for client in receivers:
    #             self.db.add_history(client, message)
    #         self.chat_arr.append(f'>>>YOU({user}): {message}')
    #     except Exception as err:
    #         client_log.error(f'Some errors in main part chat_w_message: {err}')

    def get_online(self, user, s):
        data = {
            "action": "get_contacts",  # формируем запрос по ТЗ к серверу с action "get_contacts"
            "time": datetime.timestamp(datetime.now()),
            "user": {
                "account_name": user,
            }
        }
        client_log.info(f'data for contacts: {data}')
        try:  # отправляем запрос на сервер и ожидаем ответа, тк такая информация (онлайн клиенты)
            self.send_data(data, s)  # хранится только на серверной БД
        except Exception as err:
            client_log.error(f'Some errors in chat_w_message: {err}')

    def add_contact(self, user, contact, s):
        data = {
            "action": "add_contact",  # формируем запрос по ТЗ к серверу с action "add_contact"
            "time": datetime.timestamp(datetime.now()),
            "user": {
                "account_name": user,
                "status": self.status
            },
            "contact": contact
        }
        client_log.info(f'data for contacts: {data}')
        try:
            self.send_data(data, s)
            self.db.add_contact(contact=contact)  # добавляем контакт в клиентской БД
            self.db.get_contacts()  # выводим контакты
        except Exception as err:
            client_log.error(f'Some errors in add part chat_w_message: {err}')

    def del_contact(self, user, s, contact):
        data = {
            "action": "del_contact",  # формируем запрос по ТЗ к серверу с action "add_contact"
            "time": datetime.timestamp(datetime.now()),
            "user": {
                "account_name": user,
                "status": self.status
            },
            "contact": contact
        }
        client_log.info(f'data for contacts: {data}')
        try:
            self.send_data(data, s)
            self.db.del_contacts(contact=contact)  # удаление контакта из БД на стороне клиента
            self.db.get_contacts()
        except Exception as err:
            client_log.error(f'Some errors in del part chat_w_message: {err}')

    def chat_table(self):
        self.main_window.chat_table()

    def get_receivers(self):
        contact_list = [str(name) for name in self.db.get_contacts()] # список контактов клиента, получаем из клиентской БД
        receivers = [name for name in self.online if name in contact_list]
        return receivers


# основная функция включает в себя создание сокета, тк по ТЗ мы не можем создать сокет на уровне класса
def main(addr, port, user, status):
    """основная функция для запуска клиента чата
    :param addr: server ip
    :param port: server port
    :param user: username
    :param status: user status
    :return: client run
    """
    client_log.info('client.py start...')
    client_log.info(f'Func get_addr_port...DONE, params = {addr}, {port}, {user}, {status}')
    s = create_socket_client(addr, port)  # создаем сокет
    client = Client(s, user, status)  # создаем объект класса клиент с параметрами сокета, порта, адреса

    client.run()  # запускаем клиент с помощью метода run


@log
def create_socket_client(addr, port):
    """ функция для создания сокета
    :params: addr, port
    :return s: socket
    """
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    try:
        s.connect((addr, port))  # Соединяемся с сервером
        client_log.debug(f'Create socket client. Connect to server, {addr}, {port}')
        return s
    except ConnectionRefusedError as e:
        client_log.error("Can't connect to server.")
        exit(1)


@log
def get_addr_port():
    """ функция для получения параметров из командной строки
    :return ArgumentParser()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    # parser.add_argument("-c", action="store", dest="contacts", type=str, default='')
    # parser.add_argument("-s", action="store", dest="send", type=int,
    #                     default=0)  # send дает возможность клиенту отправлять сообщения
    args = parser.parse_args()
    addr = args.addr
    port = args.port
    user = args.user
    status = args.status
    return addr, port, user, status


if __name__ == '__main__':
    try:
        main(*get_addr_port())

    except Exception:
        import sys
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
        input("Press Enter to continue ...")
