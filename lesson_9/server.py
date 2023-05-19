import argparse
import json
import logging
import select
from socket import *
from datetime import datetime
import log.server_log_config
from log.log_decorator import log

server_log = logging.getLogger('server')
print(server_log)


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
    return parser.parse_args()


@log
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
def read_requests(r_clients, all_clients):
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
def presence_answer(d):
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
def write_responses(requests, w_clients, all_clients, chat):
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
                        client.send(presence_answer(d))
                    if d['text']:  # если в сообщении есть текст
                        chat.append([d['text'], d['user']['account_name']])  # в "чат" добавляем текст и пользователя
                        for clnt in recipients:  # циклом идем по списку получателей и отправляем сообщение
                            data = {
                                "response": 200,
                                "action": "message",
                                "time": datetime.timestamp(datetime.now()),
                                "text": chat[0],
                            }
                            try:
                                send_data(data, clnt)

                            except:
                                # Сокет недоступен, клиент отключился
                                print('Клиент {} {} отключился'.format(client.fileno(), client.getpeername()))
                                client.close()
                        del chat[0]  # удаляем сообщение
                except:
                    pass


@log
def send_data(data, sock):
    """функция отправки данных
    :param sock: socket
    :param data: dict
    """
    result_data = json.dumps(data).encode('utf-8')
    sock.send(result_data)


def main():
    server_log.info('server.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    clients = []
    chat = []  # список сообщений и пользователей
    s = create_socket_server(addr, port)

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
            requests = read_requests(r, clients)  # Сохраним запросы клиентов
            if requests:
                write_responses(requests, w, clients, chat)  # Выполним отправку ответов клиентам


if __name__ == '__main__':
    main()
