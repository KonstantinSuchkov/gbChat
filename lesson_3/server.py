import argparse
import json
from socket import *
from datetime import datetime


# функция для получения параметров из командной строки
# параметры командной строки:
# -p <port> — TCP-порт для работы (по умолчанию использует 7777); -a <addr> — IP-адрес для прослушивания (по
# умолчанию слушает все доступные адреса).
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    return parser.parse_args()


def main():
    print('server.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    print(f'server params = addr: {addr}, port {port}')
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    s.bind((addr, port))  # Присваиваем порт
    s.listen(5)  # Переходим в режим ожидания запросов;

    while True:
        client, addr = s.accept()
        data = client.recv(1000000)
        d = json.loads(data.decode('utf-8'))
        if d['action'] == 'presence':
            print('Получено presence-сообщение от клиента')
            print(d)
            msg_to_client = {
                "response": 200,
                "time": datetime.timestamp(datetime.now()),
                "alert": "Code 200!!! Code 200"
            }
            msg = json.dumps(msg_to_client, indent=4).encode('utf-8')
            client.send(msg)
            print('Сообщение: ', msg.decode('utf-8'), ', было отправлено клиенту: ', addr, port)

        client.close()


if __name__ == '__main__':
    main()

# server.py start... server params = addr: , port 7777 Получено presence-сообщение от клиента {'action': 'presence',
# 'time': 1681104234.028539, 'type': 'status', 'user': {'account_name': 'Varvara', 'status': '2 years'}} Сообщение:
# { "response": 200, "time": 1681104234.029506, "alert": "Code 200!!! Code 200" } , было отправлено клиенту:  (
# '127.0.0.1', 63540) 7777
