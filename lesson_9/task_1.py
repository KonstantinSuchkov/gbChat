# Задание 9
# 1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых
# узлов. Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
# ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
# сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью
# функции ip_address().
import ipaddress
import platform
import socket
import string
import subprocess


def host_ping(list_addr):
    """func for ping addresses
    :param list_addr:
    :return: dict {'Reachable': [], 'Unreachable': []}
    """
    param = '-n 1' if platform.system().lower() == 'windows' else '-c'
    result = {'Reachable': [], 'Unreachable': []}
    for addr in list_addr:
        try:
            s = addr.translate(str.maketrans('', '', string.punctuation))  # убираем точки из адреса для проверки
            if s.isdigit():  # если адрес без точек isdigit, значит это ip адрес
                address = ipaddress.ip_address(addr)  # ip-адрес сетевого узла должен создаваться с помощью
# функции ip_address().
            else:
                address = ipaddress.ip_address(socket.gethostbyname(addr))  # иначе это имя сайта, получаем ip адрес
            args = "ping " + param + " " + str(address)
            con_out = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT).decode('cp866')
            if con_out:
                print(f'Узел доступен: {addr}')
                result['Reachable'].append(addr)
        except Exception:
            print(f'Узел недоступен: {addr}')
            result['Unreachable'].append(addr)
            pass
    return result


if __name__ == '__main__':
    host_ping(['8.8.8.8', '127.0.0.1', '111.22.33.44.55', 'yandex.ru'])

# Узел доступен: 8.8.8.8
# Узел доступен: 127.0.0.1
# Узел недоступен: 111.22.33.44.55
# Узел доступен: yandex.ru
