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
    # data = ['some_data', 22113]  # wrong type data
    return data


# функция для получения параметров из командной строки
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    return parser.parse_args()


def create_socket_client(addr, port):
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    try:
        s.connect((addr, port))  # Соединяемся с сервером
        return s
    except ConnectionRefusedError as e:
        print("Can't connect to server. Check port")
        exit(1)

def read_answer(dict_from_server):
    return dict_from_server['response'], dict_from_server['alert']


def main():
    print('client.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    user = args.user
    status = args.status
    print(f'params = {addr}, {port}, {user}, {status}')
    s = create_socket_client(addr, port)
    presence_msg = presence(user, status)  # создаем presence-сообщение
    s.send(json.dumps(presence_msg, indent=4).encode('utf-8'))
    try:
        data = s.recv(1000000)
        d = json.loads(data.decode('utf-8'))
        print('Сообщение от сервера: ', read_answer(d))
    except:
        print('Сообщений нет')

    s.close()


if __name__ == '__main__':
    main()

# client.py start...
# params = localhost, 7777, Varvara, 2 years
# Сообщение от сервера:  200 Code 200!!! Code 200
