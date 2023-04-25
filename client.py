# Программа клиента для отправки приветствия серверу и получения ответа
import argparse
import logging
from socket import *
from datetime import datetime
import json
import log.client_log_config
from log.log_decorator import log

client_log = logging.getLogger('client')


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


@log
def message_to_server(message, account_name):
    data = {
        "action": "message",
        "time": datetime.timestamp(datetime.now()),
        "text": message,
        "user": {
            "account_name": account_name,
        }
    }
    return data


@log
def data_from_server(sock):
    received_data = sock.recv(10000000)
    decoded_data = received_data.decode('utf-8')
    result_data = json.loads(decoded_data)
    if type(result_data) == dict:
        return result_data
    return {}


@log
def send_data(data, sock):
    result_data = json.dumps(data).encode('utf-8')
    sock.send(result_data)


# функция для получения параметров из командной строки
@log
def get_addr_port():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    parser.add_argument("-s", action="store", dest="send", type=int,
                        default=0)  # send дает возможность клиенту отправлять сообщения
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
        client_log.error("Can't connect to server.")
        exit(1)


@log
def read_answer(dict_from_server):
    try:
        response_code = dict_from_server.get('response', 0)
    except Exception as err:
        client_log.error(f'Error {err})')
    else:
        if response_code:
            if response_code == 200:
                result_msg = dict_from_server.get('alert', 'OK.')
                client_log.info('Response status OK')
                try:
                    result_msg = dict_from_server.get('text', 0)  # пробуем достать текст сообщения
                except Exception as err:
                    client_log.error(f'Error {err})')
                else:
                    if result_msg:
                        return f'{result_msg[0]} by {result_msg[1]}'  # если есть текст выводим сообщение и автора
            else:
                result_msg = dict_from_server.get('error', 'unknown error')
                client_log.info(f'Status: {response_code}: {result_msg}')
            return f'{response_code}: {result_msg}'
        client_log.error(f'Data : {dict_from_server}')
    return ''


def main():
    client_log.info('client.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    user = args.user
    send_ok = args.send  # параметр, определяющий возможность отправлять сообщения
    status = args.status
    client_log.info(f'Func get_addr_port...DONE, params = {addr}, {port}, {user}, {status}')

    s = create_socket_client(addr, port)  # создаем сокет
    presence_msg = presence(user, status)  # создаем presence-сообщение
    client_log.info('Presence message sending...')
    send_data(presence_msg, s)
    client_log.info('Presence message sending...DONE')
    try:
        data = data_from_server(s)
        answer = read_answer(data)
        client_log.info('Message(answer) from server received: ')
        print(f'Message(answer) from server received: ', answer)

    except:
        client_log.error('No messages from server.')

    if send_ok:  # если параметр send, то ожидаем от клиента ввода сообщения
        while True:
            message = input('Write text to sending: ')
            try:
                send_data(message_to_server(message, user), s)
            except Exception as err:
                client_log.error(f'Some errors: {err}')
    else:  # если параметра send нет, то ожидаем входящих сообщений
        print('client send status 0, waiting messages...')
        while True:
            try:
                print('waiting...')
                data = data_from_server(s)
                print(f'data from server : {data}')
                answer = read_answer(data)
                client_log.info(f'{user} - Message(answer) from server received: ')
                print(f'Message(answer) from server received: ', answer)
            except Exception as err:
                client_log.error(f'Some errors: {err}')



if __name__ == '__main__':
    main()

# client.py start...
# params = localhost, 7777, Varvara, 2 years
# Сообщение от сервера:  200 Code 200!!! Code 200
