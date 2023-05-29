import argparse
import json
import logging
import select
import threading
from dis import get_instructions
from socket import *
from datetime import datetime

from PyQt5.QtCore import QTimer

import log.server_log_config
from log.log_decorator import log

from store import StoreServer
from server_app import *

server_log = logging.getLogger('server')
print(server_log)


# дескриптор
class ServerPort:
    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            raise ValueError(f'Wrong port: {value}')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


# метакласс(задание 2 к уроку 10)
class ServerVerifier(type):

    def __init__(cls, classname, bases, dict):

        for func in dict:
            try:
                instructions = get_instructions(dict[func])
            except TypeError:
                pass
            else:
                for op in instructions:
                    if op.opname == 'LOAD_GLOBAL':
                        if op.argval in ('accept', 'listen'):
                            raise TypeError(f'{op.argval} cant use in class Server')

        super().__init__(classname, bases, dict)


# Основной класс серверной части чата
class Server(threading.Thread, metaclass=ServerVerifier):
    port = ServerPort()  # инициализация класса-дескриптора для проверки и установки значения порта

    def __init__(self, addr, port, db_name):
        self.addr = addr
        self.port = port
        self.db = StoreServer(db_name)
        super().__init__()

    @staticmethod
    def create_socket_server(addr, port):
        """ функция создания сокета сервера
        :params: server port and address
        :return: s:socket
        """
        print(f'server params = addr: {addr}, port {port}')
        server_log.info(f'Create socket server. Server params -- addr: {addr}, port {port}')
        s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
        s.bind((addr, port))  # Присваиваем адрес, порт
        s.listen(5)
        s.settimeout(1.5)  # Таймаут для операций с сокетом
        return s

    def read_requests(self, r_clients, all_clients, users):
        """ Чтение запросов из списка клиентов
        :params: clients (get from select)
        :return: dict {socket: data}
        """
        responses = {}  # Словарь ответов сервера вида {сокет: запрос}
        for sock in r_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                responses[sock] = data
            except:  # сокет отключился
                server_log.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                # all_clients.remove(sock)
                for u in list(users):  # обход циклом словарь клиентов {клиент: сокет}
                    if sock == users[u]:  # если сокет в словаре
                        self.db.client_disconnect(u)  # метод изменяет параметр клиента online на значение False
                        r_clients.remove(sock)  # удаляем socket из списка сокетов клиентов
                        _ = users.pop(u, None)  # удаление юзера-клиента из именного словаря клиентов
        return responses

    @log
    def presence_answer(self, d):
        """ формирование ответа клиенту на presense сообщение
        :params: dict
        :return: message bytes
        """
        msg = {
            "response": 200,
            "time": datetime.timestamp(datetime.now()),
            "alert": "OK"
        }
        msg = json.dumps(msg, indent=4).encode('utf-8')
        return msg

    def write_responses(self, requests, w_clients, clients, chat, users):
        """ ответ сервера клиентам
        :params: clients requests, clients, chat(list of messages)
        result: send message to clients or presence answer
        """
        for client in w_clients:
            if client in requests:
                resp = requests[client].encode('utf-8')
                if resp != b'':
                    d = json.loads(resp.decode('utf-8'))
                    try:
                        if d['action'] == 'presence':  # если сообщение presence, то отправляем соответствующий ответ
                            client.send(self.presence_answer(d))
                            login = d['user']['account_name']
                            info = d['user']['status']
                            self.db.client_login(login=login, info=info, ip=self.port, online=True, contacts=None)
                            users[d['user']['account_name']] = client  # добавляем клиента в базу

                        if d['action'] == 'get_contacts':
                            try:
                                contacts = self.db.get_online()
                                result = []
                                for i in contacts:
                                    for x in i:
                                        result.append(str(x))
                                data = {
                                    "response": 202,
                                    "alert": result,
                                }
                                self.send_data(data, client)
                            except:
                                pass

                        if d['action'] == 'add_contact':  # клиент ввел команду на добавление контакта
                            login = d['user']['account_name']
                            contact = d['contact']
                            try:
                                self.db.add_contact(login=login, contact=contact)  # добавляем контакт в серверной БД
                                client.send(self.presence_answer(d))
                            except:
                                pass

                        if d['action'] == 'del_contact':  # клиент ввел команду на удаление контакта
                            login = d['user']['account_name']
                            contact = d['contact']
                            try:
                                self.db.del_contacts(login=login, contact=contact)  # удаление контакта в серверной БД
                                client.send(self.presence_answer(d))
                            except:
                                pass

                        if d['text'] == 'Hello World':  # тестовое сообщение клиента для ответа только самому клиенту
                            chat.append(['Hi, Bro!', d['user']['account_name']])
                            data = {
                                "response": 200,
                                "action": "message",
                                "time": datetime.timestamp(datetime.now()),
                                "text": chat[0],
                            }
                            try:
                                self.send_data(data, client)
                            except:
                                # Сокет недоступен, клиент отключился
                                pass
                            del chat[0]  # удаляем сообщение

                        if d['text'] and d['text'] != 'Hello World':  # если в сообщении есть текст
                            login = d['user']['account_name']
                            client_list = self.db.get_contacts(login=login)
                            # Ниже создаем список получателей из словаря users(клиенты онлайн) и списка client_list
                            # т.е. сообщение будет отправлено только тем, кто онлайн и в контактах отправителя
                            receivers = {name: users[name] for name in client_list if name in users}
                            chat.append([d['text'], login])
                            for key, value_sock in receivers.items():  # идем циклом по значению словаря (сокетам)
                                data = {
                                    "response": 200,
                                    "action": "message",
                                    "time": datetime.timestamp(datetime.now()),
                                    "text": chat[0],
                                }
                                try:
                                    self.send_data(data, value_sock)
                                    history_rec = self.db.MessageHistory(author=login, recipient=key, text=chat[0][0])
                                    self.db.session.add(history_rec)
                                    self.db.session.commit()
                                except:
                                    # Сокет недоступен, клиент отключился
                                    pass
                            del chat[0]  # удаляем сообщение
                    except:
                        pass

    @log
    def send_data(self, data, sock):
        """функция отправки данных
        :param sock: socket
        :param data: dict
        """
        result_data = json.dumps(data).encode('utf-8')
        sock.send(result_data)

    # основной метод класса с серверной логикой чата
    def main(self):
        server_log.info('server.py start...')
        clients = []  # список сокетов клиентов
        chat = []  # список сообщений и пользователей
        users = {}  # словарь {Username: socket}
        s = self.create_socket_server(self.addr, self.port)

        while True:
            try:
                conn, addr = s.accept()  # Проверка подключений
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                clients.append(conn)
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                requests = self.read_requests(r, clients, users)  # Сохраним запросы клиентов
                if requests:
                    self.write_responses(requests, w, clients, chat, users)  # Выполним отправку ответов клиентам
                    print(f'Clients online: {self.db.get_online()}')  # вывод находящихся онлайн пользователей
                    # requests = {}

    def admin_commands(self):  # функция для администрирования серверной части чата, ввода команд
        while True:
            command = input('введите команду\n')
            if command == 'exit':
                exit()
            elif command == 'online':
                print(f'Clients online: {self.db.get_online()}')
            elif command == 'h':
                login = input('введите логин клиента\n')
                print(f'Client hystory: {self.db.get_history(login, last_entry=True)}')
            else:
                print('What u mean, bro?')


# вспомогательная функция
def get_addr_port():
    """ получение (парсинг) аргументов
    -a -> addr
    -p -> port
    :return ArgumentParser()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    args = parser.parse_args()
    addr = args.addr
    port = args.port
    return addr, port


# GUI Functions
def refresh_table():
    main_window.table(db=server.db)


def on_clicked():
    print("Поздравляю! Твоя первая кнопка нажата!")


def all_clients(db):
    s = db.get_clients()
    raw_s = r'{}'.format(s)
    print(raw_s)


def on_line(db):
    res = db.get_online()
    if res:
        s = ''.join(res[0])
        raw_s = r'{}'.format(s)
        print(raw_s)
    else:
        print('No online client')


def save_config(config_window):
    new_settings = config_window.setting_dict()
    with open('server_settings.json', 'w', encoding='utf-8') as f:
        json.dump(new_settings, f)
    config_window.close()


if __name__ == '__main__':
    # сначала запускаем окно настроек
    server_app = QApplication(sys.argv)
    config_window = ConfigWindow({})
    config_window.ok_button.clicked.connect(lambda _: save_config(config_window))
    server_app.exec_()
    with open('server_settings.json', 'r', encoding='utf-8') as f_r:  # полученные из ConfigWindow настройки в файл
        settings = json.load(f_r)  # полученные из ConfigWindow настройки передаем в файл
        f_r.close()

    # запуск сервера через командную строку
    # server = Server(*get_addr_port())

    # после получения настроек используем их для запуска сервера
    server = Server(addr=settings['addr'], port=settings['port'],
                    db_name=settings['db_name'])  # запуск сервера через приложение

    threading_1 = threading.Thread(daemon=True, target=server.main)
    threading_1.start()  # запускаем первый поток с основным методом класса Server

    threading_2 = threading.Thread(target=server.admin_commands)
    threading_2.daemon = True
    threading_2.start()  # определяем второй поток для возможности ввода команд

    main_window = MainWindow()

    # таймер для обновления отображения данных в приложении
    timer = QTimer()
    timer.timeout.connect(refresh_table)
    timer.start(1000)

    main_window.just_button.triggered.connect(on_clicked)  # тестовая кнопка
    main_window.all_clients.triggered.connect(lambda: main_window.online_clients(db=server.db))  # клиенты-онлайн
    main_window.online.triggered.connect(lambda _: main_window.history_table(db=server.db))  # история сообщений
    main_window.statusBar().showMessage('Lets go!')  # статус-бар

    server_app.exec_()
    server.admin_commands()
