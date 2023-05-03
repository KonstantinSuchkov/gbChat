# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
# последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.

# Октет — 8-битный номер, 4 из которых составляют 32-битный IP-адрес. Они имеют диапазон 00000000-11111111,
# соответствующий десятичным значениям 0–255.
from task_1 import host_ping


def host_range_ping(ip_addr, rng):
    """
    :param ip_addr: ip address for ping
    :param rng: interval range for last octet
    :return: str
    """
    octets = ip_addr.split('.')  # делаем список из аргумента ip_addr для дальнейшей работы
    last_octet = int(octets[-1])  # находим и записываем последний октет, который будет меняться по условиям задачи
    result_list = [ip_addr]  # записываем в результирующий список начальный ip адрес
    for i in range(rng):  # идем циклом в заданном интервале
        result = last_octet + (i + 1)  # получаем новое значение последнего октета
        octets[-1] = result  # меням последний октет на новое значение
        s = '.'.join(str(x) for x in octets)  # создаем строку-ip адрес с новым последним октетом
        result_list.append(s)  # добавляем новый ip-адрес в результирующий список
    return host_ping(result_list)  # по окончании цикла передаем результирующий список в функцию для пинга адресов


if __name__ == '__main__':
    host_range_ping('127.0.0.251', 5)
# Узел доступен: 127.0.0.251
# Узел доступен: 127.0.0.252
# Узел доступен: 127.0.0.253
# Узел доступен: 127.0.0.254
# Узел доступен: 127.0.0.255
# Узел недоступен: 127.0.0.256
