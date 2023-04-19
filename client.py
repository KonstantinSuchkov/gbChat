# Программа клиента для отправки приветствия серверу и получения ответа
import argparse
import logging
from socket import *
from datetime import datetime
import json
import log.client_log_config
from log.log_decorator import log


client_log = logging.getLogger('client')
print(client_log)


# функция для формирования presence-сообщения
@log
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
@log
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    client_log.debug('Func get_addr_port start...')
    return parser.parse_args()


@log
def create_socket_client(addr, port):
    s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP
    try:
        s.connect((addr, port))  # Соединяемся с сервером
        client_log.debug(f'Create socket client. Connect to server, {addr}, {port}')
        return s
    except ConnectionRefusedError as e:
        client_log.error("Can't connect to server. Check port")
        exit(1)


@log
def read_answer(dict_from_server):
    client_log.info('Reading answer from server(func read_answer)')
    return dict_from_server['response'], dict_from_server['alert']


def main():
    client_log.info('client.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    user = args.user
    status = args.status
    client_log.info(f'Func get_addr_port...DONE, params = {addr}, {port}, {user}, {status}')
    s = create_socket_client(addr, port)
    presence_msg = presence(user, status)  # создаем presence-сообщение
    client_log.info('Presence message sending...')
    s.send(json.dumps(presence_msg, indent=4).encode('utf-8'))
    client_log.info('Presence message sending...DONE')
    try:
        data = s.recv(1000000)
        d = json.loads(data.decode('utf-8'))
        answer = read_answer(d)
        client_log.info('Message(answer) from server received: ')
        print(f'Message(answer) from server received: ', answer)
        s.close()
    except:
        client_log.error('No messages from server.')
        s.close()

    s.close()


if __name__ == '__main__':
    main()

# client.py start...
# params = localhost, 7777, Varvara, 2 years
# Сообщение от сервера:  200 Code 200!!! Code 200
