import argparse
import json
import logging
import select
from dis import get_instructions
from socket import *
from datetime import datetime
import log.server_log_config
from log.log_decorator import log

server_log = logging.getLogger('server')
print(server_log)


# Lesson 10.2. Реализовать метакласс ServerVerifier, выполняющий базовую проверку класса «Сервер»: отсутствие вызовов
# connect для сокетов; использование сокетов для работы по TCP. ### 3. Реализовать дескриптор для класса серверного
# сокета, а в нем — проверку номера порта. Это должно быть целое число (>=0). Значение порта по умолчанию равняется
# 7777. Дескриптор надо создать в отдельном классе. Его экземпляр добавить в пределах класса серверного сокета. Номер
# порта передается в экземпляр дескриптора при запуске сервера.


# дескриптор
class ServerPort:
    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            raise ValueError(f'Wrong port: {value}')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


# (venv) PS C:\Users\vanka\PycharmProjects\gbChat> python server.py -p ff
# <Logger server (DEBUG)>
# usage: server.py [-h] [-a ADDR] [-p PORT]
# server.py: error: argument -p: invalid int value: 'ff'

# (venv) PS C:\Users\vanka\PycharmProjects\gbChat> python server.py -p 1
# <Logger server (DEBUG)>
# Traceback (most recent call last):
#   File "C:\Users\vanka\PycharmProjects\gbChat\server.py", line 198, in <module>
#     server = Server(*get_addr_port())
#   File "C:\Users\vanka\PycharmProjects\gbChat\server.py", line 58, in __init__
#     self.port = port
#   File "C:\Users\vanka\PycharmProjects\gbChat\server.py", line 27, in __set__
#     raise ValueError(f'Wrong port: {value}!')
# ValueError: Wrong port: 1


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
class Server(metaclass=ServerVerifier):
    port = ServerPort()  # инициализация класса-дескриптора для проверки и установки значения порта

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

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

    @log
    def read_requests(self, r_clients, all_clients):
        """ Чтение запросов из списка клиентов
        :params: clients (get from select)
        :return: dict {socket: data}
        """
        responses = {}  # Словарь ответов сервера вида {сокет: запрос}
        for sock in r_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                responses[sock] = data
            except:
                server_log.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)
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

    @log
    def write_responses(self, requests, w_clients, all_clients, chat):
        """ ответ сервера клиентам
        :params: clients requests, clients, chat(list of messages)
        result: send message to clients or presence answer
        """
        for client in w_clients:
            if client in requests:
                resp = requests[client].encode('utf-8')
                recipients = all_clients.copy()  # создаем список получателей
                recipients.remove(client)  # исключаем из получателей клиента-отправителя
                if resp != b'':
                    d = json.loads(resp.decode('utf-8'))
                    try:
                        if d['action'] == 'presence':  # если сообщение presence, то отправляем соответствующий ответ
                            client.send(self.presence_answer(d))
                        if d['text']:  # если в сообщении есть текст
                            chat.append(
                                [d['text'], d['user']['account_name']])  # в "чат" добавляем текст и пользователя
                            for clnt in recipients:  # циклом идем по списку получателей и отправляем сообщение
                                data = {
                                    "response": 200,
                                    "action": "message",
                                    "time": datetime.timestamp(datetime.now()),
                                    "text": chat[0],
                                }
                                try:
                                    self.send_data(data, clnt)

                                except:
                                    # Сокет недоступен, клиент отключился
                                    print('Клиент {} {} отключился'.format(client.fileno(), client.getpeername()))
                                    client.close()
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
        clients = []
        chat = []  # список сообщений и пользователей
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
                requests = self.read_requests(r, clients)  # Сохраним запросы клиентов
                if requests:
                    self.write_responses(requests, w, clients, chat)  # Выполним отправку ответов клиентам


# вспомогательная функция
@log
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


if __name__ == '__main__':
    server = Server(*get_addr_port())
    server.main()
