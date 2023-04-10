# Программа клиента для отправки приветствия серверу и получения ответа
import argparse
from socket import *
from datetime import datetime
import json


# функция для формирования presence-сообщения
def presence(account_name, status):
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


# функция для получения параметров из командной строки
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    return parser.parse_args()


def main():
    print('client.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    user = args.user
    status = args.status
    print(f'params = {addr}, {port}, {user}, {status}')
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    s.connect((addr, port))  # Соединяемся с сервером
    presence_msg = presence(user, status)  # создаем presence-сообщение
    s.send(json.dumps(presence_msg, indent=4).encode('utf-8'))
    try:
        data = s.recv(1000000)
        d = json.loads(data.decode('utf-8'))
        print('Сообщение от сервера: ', d['response'], d['alert'])
    except:
        print('Сообщений нет')

    s.close()


if __name__ == '__main__':
    main()

# client.py start...
# params = localhost, 7777, Varvara, 2 years
# Сообщение от сервера:  200 Code 200!!! Code 200
