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


# функция для получения параметров из командной строки
# параметры командной строки:
# -p <port> — TCP-порт для работы (по умолчанию использует 7777); -a <addr> — IP-адрес для прослушивания (по
# умолчанию слушает все доступные адреса).
@log
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    return parser.parse_args()


@log
def create_socket_server(addr, port):
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
def msg_to_client(d):
    if d['action'] == 'presence':
        msg = {
            "response": 200,
            "time": datetime.timestamp(datetime.now()),
            "alert": "OK"
        }
        msg = json.dumps(msg, indent=4).encode('utf-8')
        return msg
    else:
        print(f"message: {d['text']} from {d['user']['account_name']}")
        data = {
            "response": 200,
            "action": "message",
            "time": datetime.timestamp(datetime.now()),
            "text": d['text'],
            "user": {
                "account_name": d['user']['account_name'],
            }
        }
        msg = json.dumps(data, indent=4).encode('utf-8')
        return msg


@log
def write_responses(requests, w_clients, all_clients, chat):
    """ ответ сервера клиентам
    """
    for client in w_clients:
        if client in requests:
            resp = requests[client].encode('utf-8')
            if resp != b'':
                d = json.loads(resp.decode('utf-8'))
                try:
                    if d['text']:
                        chat.append([d['text'], d['user']['account_name']])  # добавляем сообщение и пользователя
                except:
                    pass
                try:
                    client.send(msg_to_client(d))
                    print('sending')
                except:
                    # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(client.fileno(), client.getpeername()))
                    client.close()
                    all_clients.remove(client)


@log
def send_data(data, sock):
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
            if chat:  # если есть сообщения, то выполнится отправка клиентам
                for client in clients:
                    data = {
                        "response": 200,
                        "action": "message",
                        "time": datetime.timestamp(datetime.now()),
                        "text": chat[0],
                    }
                    send_data(data, client)
                del chat[0]


if __name__ == '__main__':
    main()
