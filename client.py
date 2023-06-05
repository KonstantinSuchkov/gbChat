import argparse
import ast
import binascii
import hashlib
import logging
import os
import queue
import time
from socket import *
from datetime import datetime
import json
from threading import Thread

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys
import log.client_log_config
from client_app import MainClientWindow, AuthWindow
from log.log_decorator import log
from dis import get_instructions

from server import on_clicked
from settings import SALT
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
    def __init__(self, s, user, status, hash_item):
        self.messages_list = []
        self.s = s
        self.user = user
        self.status = status
        self.hash_item = hash_item
        self.db = None
        self.main_window = None
        self.online = []
        self.timer = QTimer()
        self.chat_arr = []
        self.q = queue.Queue()
        self.keys = {}  # публичные ключи других клиентов для сквозного шифрования
        self.privateKey = None
        self.publicKey = None

    def run(self):
        """
        Основной метод класса с логикой чата
        :return:
        """
        print(f'client {self.user} starting...')
        client_log.info(f'client {self.user} starting...')
        # Блок авторизации, создание ключей для ассиметричного шифрования
        self.send_data(self.check_password(), self.s)
        while True:
            try:
                data = self.data_from_server(self.s)
                answer = self.read_answer(data)
                print(answer)
                client_log.info(f'Message from Server received: {answer} ')

                key = RSA.generate(2048)
                self.privateKey = key.export_key()
                self.publicKey = key.publickey().export_key()

                # # save private key to file
                # with open(f'db/{self.user}_client_private.pem', 'wb') as f:
                #     f.write(privateKey)
                #
                # # save public key to file
                # with open(f'db/{self.user}_client_public.pem', 'wb') as f:
                #     f.write(publicKey)

                presence_msg = self.presence(self.user, self.status, self.publicKey.decode('ascii'))  # создаем presence-сообщение
                print('Presence message sending...')
                client_log.info('Presence message sending...')
                self.send_data(presence_msg, self.s)
                client_log.info('Presence message sending...DONE')
                print('Presence message sending...DONE')
            except Exception as err:
                client_log.error(f'Some errors in authentification: {err}')
                exit(1)
            # Авторизация прошла

            self.db = StoreClient(self.user)
            print(f'{self.user} data base init...')
            client_log.info(f'{self.user} data base init...')

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
                print(answer)
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

    def check_password(self):
        data = {
            "action": "checking",
            "time": datetime.timestamp(datetime.now()),
            "user": {
                "account_name": self.user,
                "status": self.status,
                "hash": str(self.hash_item)
            }
        }
        return data

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
                        print('result_msg', result_msg)
                        rsa_private_key = RSA.importKey(self.privateKey)
                        rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
                        decrypted = rsa_private_key.decrypt(ast.literal_eval(result_msg[0]))
                        print('decrypted', decrypted)
                        decrypted = decrypted.decode('utf-8')

                        return f'>>>{result_msg[1]}: {decrypted}'  # если есть текст выводим сообщение и автора

                    except Exception as err:
                        client_log.error(f'Error {err})')
                        print(f'error in read_answer: {err}')

                    return f'{response_code}: {result_msg}'

                if response_code == 202:
                    try:
                        result_msg = dict_from_server.get('alert')  # пробуем достать сообщение
                        keys = dict_from_server.get('keys')
                    except Exception as err:
                        client_log.error(f'Error {err})')
                    else:
                        if result_msg:
                            self.online = result_msg  # записываем всех клиентов, полученных с сервера в список
                            self.keys = keys  # обновляем ключи клиентов для шифрования
                            return f'>>>{result_msg}'

                if response_code == 401:
                    try:
                        print('Wrong auth, check username or password')
                        client_log.info(f'Wrong auth for client{self.user}')
                        exit(1)
                    except Exception as err:
                        client_log.error(f'Error {err})')

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
    def presence(account_name, status, publicKey):
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
                "status": status,
                "pub_key": publicKey
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


    def message_to_server(self, message, author, receiver):
        """ функция(метод) для формирования сообщения
        :params: message: text, account_name
        :return: dict
        """
        data = {
            "action": "message",
            "time": datetime.timestamp(datetime.now()),
            "receivers": receiver,
            "user": {
                "account_name": author,
            },
            "text": message,
        }
        return data

    # GUI and other Functions
    def refresh_table(self):
        self.main_window.table(db=self.db, online=self.online, chat_arr=self.chat_arr)

    def main_send_message(self, message, user, s):
        self.messages_list.append(message)
        if self.messages_list != []:
            try:  # стандартный протокол отправки сообщения на сервер
                receivers = self.get_receivers()
                for client in receivers:

                    client_pub_key = self.keys[client]
                    message_prepare = str.encode(message)
                    rsa_public_key = RSA.importKey(client_pub_key)
                    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
                    encrypted_text = rsa_public_key.encrypt(message_prepare)

                    self.send_data(self.message_to_server(str(encrypted_text), user, client), s)

                    if type(message) is list:
                        self.db.add_history(client, message[0])
                    else:
                        self.db.add_history(client, message)

                self.chat_arr.append(f'>>>YOU({user}): {message}')  # отобразить свое собственное сообщение в чате
                del self.messages_list[-1]
            except Exception as err:
                client_log.error(f'Some errors in main part chat_w_message: {err}')

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
            self.send_data(data, s)  # хранится только на сервере
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
def main(addr, port, user, status, password):
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
    client = Client(s, user, status, password)  # создаем объект класса клиент с параметрами сокета, порта, адреса

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
    # parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    # parser.add_argument("-c", action="store", dest="contacts", type=str, default='')
    # parser.add_argument("-s", action="store", dest="send", type=int,
    #                     default=0)  # send дает возможность клиенту отправлять сообщения
    args = parser.parse_args()
    addr = args.addr
    port = args.port
    # user = args.user
    status = args.status
    window = AuthWindow()  # запускается окно ввода логина
    if window.exec():  # при закрытии окна значения полей формируют параметры для дальнейшего запуска клиента
        user = window.name_field.text()
        password = window.passw_field.text()
        salt = password + SALT
        salt = salt.encode('utf-8')
        password_bytes = password.encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        hash_item = binascii.hexlify(key)
        if window.info.text() != '':
            status = window.info.text()

        return addr, port, user, status, hash_item


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main(*get_addr_port())
        app.exec_()

    except Exception:
        import sys
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
        input("Press Enter to continue ...")
