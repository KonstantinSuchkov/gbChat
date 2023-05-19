# Программа клиента для отправки приветствия серверу и получения ответа
import argparse
import logging
import time
from socket import *
from datetime import datetime
import json
from threading import Thread

import log.client_log_config
from log.log_decorator import log

client_log = logging.getLogger('client')


@log
def presence(account_name, status):
    """ функция для формирования presence-сообщения
    :params: account_name, status
    :return: dict
    """
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
    """ функция для формирования сообщения
    :params: message: text, account_name
    :return: dict
    """
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
    """ функция для преобразования ответа с сервера в словарь
    :params: sock: socket
    :return: dict
    """
    received_data = sock.recv(10000000)
    decoded_data = received_data.decode('utf-8')
    result_data = json.loads(decoded_data)
    if type(result_data) == dict:
        return result_data
    return {}


@log
def send_data(data, sock):
    """функция отправки данных
    :param sock: socket
    :param data: dict
    """
    result_data = json.dumps(data).encode('utf-8')
    sock.send(result_data)


@log
def get_addr_port():
    """ функция для получения параметров из командной строки
    :return ArgumentParser()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", action="store", dest="addr", type=str, default='localhost')
    parser.add_argument("-p", action="store", dest="port", type=int, default=7777)
    parser.add_argument("-user", action="store", dest="user", type=str, default='Varvara')
    parser.add_argument("-status", action="store", dest="status", type=str, default='2 years')
    # parser.add_argument("-s", action="store", dest="send", type=int,
    #                     default=0)  # send дает возможность клиенту отправлять сообщения
    client_log.debug('Func get_addr_port start...')
    return parser.parse_args()


@log
def create_socket_client(addr, port):
    """ функция для создания сокета
    :params: addr, port
    :return s: socket
    """
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
    """ функция для считывания ответа из данных (словаря), поступивших с сервера
    :params: dict
    :return str: >>>{username}: {text}
    """
    try:
        response_code = dict_from_server.get('response', 0)
    except Exception as err:
        client_log.error(f'Error {err})')
    else:
        if response_code:
            if response_code == 200:  # проверяем код
                result_msg = dict_from_server.get('alert', 'OK.')
                client_log.info('Response status OK')
                try:
                    result_msg = dict_from_server.get('text', 0)  # пробуем достать текст сообщения
                except Exception as err:
                    client_log.error(f'Error {err})')
                else:
                    if result_msg:
                        return f'>>>{result_msg[1]}: {result_msg[0]}'  # если есть текст выводим сообщение и автора
            else:
                result_msg = dict_from_server.get('error', 'unknown error')
                client_log.info(f'Status: {response_code}: {result_msg}')
            return f'{response_code}: {result_msg}'
        client_log.error(f'Data : {dict_from_server}')
    return ''


def chat_r_message(sock):
    """ функция отображения сообщений других пользователей, для работы в режиме "многопоточности".
    Пока клиент запущен будем ожидать сообщений от других клиентов
    :params: sock: socket
    """
    while True:
        try:
            data = data_from_server(sock)
            answer = read_answer(data)
            print(answer)
            client_log.info(f'Message received: {answer} ')
        except Exception as err:
            client_log.error(f'Some errors: {err}')
            exit(1)


def chat_w_message(user, s):
    """ функция отправки сообщений другим пользователям, для работы в режиме "многопоточности".
    Пока клиент запущен будем ожидать ввода сообщения от пользователя
    :params: sock: socket
    """
    while True:
        message = input(f'>>>{user}\n')
        try:
            send_data(message_to_server(message, user), s)
        except Exception as err:
            client_log.error(f'Some errors: {err}')


def main():
    client_log.info('client.py start...')
    args = get_addr_port()  # получаем параметры из командной строки -p -a
    addr = args.addr
    port = args.port
    user = args.user
    # send_ok = args.send  # параметр, определяющий возможность отправлять сообщения
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
        print(f'Message(answer) from server received: ', answer)

    except:
        client_log.error('No messages from server.')
        exit(1)

    w = Thread(target=chat_w_message, args=(user, s))
    w.daemon = True
    w.start()

    r = Thread(target=chat_r_message, args=(s,))
    r.daemon = True
    r.start()

    while True:
        time.sleep(1)
        if not w.is_alive() or not r.is_alive():
            break


if __name__ == '__main__':
    main()
