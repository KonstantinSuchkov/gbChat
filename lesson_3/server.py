import argparse
import json
from socket import *
from datetime import datetime
import logging

server_log = logging.getLogger('server')


# функция для получения параметров из командной строки
# параметры командной строки:
# -p <port> — TCP-порт для работы (по умолчанию использует 7777); -a <addr> — IP-адрес для прослушивания (по
# умолчанию слушает все доступные адреса).
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    return parser.parse_args()


def create_socket_server(addr, port):
    print(f'server params = addr: {addr}, port {port}')
    server_log.info(f'server params = addr: {addr}, port {port}')
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    s.bind((addr, port))  # Присваиваем адрес, порт
    s.listen(5)
    return s


def msg_to_client(d, client):
    if d['action'] == 'presence':
        server_log.info('Получено presence-сообщение от клиента')
        print('Получено presence-сообщение от клиента')
        msg = {
            "response": 200,
            "time": datetime.timestamp(datetime.now()),
            "alert": "Code 200!!! Code 200"
        }
        msg = json.dumps(msg, indent=4).encode('utf-8')
        client.send(msg)
        print('Сообщение: ', msg.decode('utf-8'), ', было отправлено клиенту')
        server_log.info('Сообщение: ', msg.decode('utf-8'), ', было отправлено клиенту')


def main():
    print('server.py start...')
    server_log.info('server.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    s = create_socket_server(addr, port)

    while True:
        client, addr = s.accept()
        try:
            data = client.recv(1000000)
            d = json.loads(data.decode('utf-8'))
            msg_to_client(d, client)
            client.close()
        except Exception as err:
            print('Wrong data!:', err)
            client.close()

if __name__ == '__main__':
    main()

# server.py start... server params = addr: , port 7777 Получено presence-сообщение от клиента {'action': 'presence',
# 'time': 1681104234.028539, 'type': 'status', 'user': {'account_name': 'Varvara', 'status': '2 years'}} Сообщение:
# { "response": 200, "time": 1681104234.029506, "alert": "Code 200!!! Code 200" } , было отправлено клиенту:  (
# '127.0.0.1', 63540) 7777
