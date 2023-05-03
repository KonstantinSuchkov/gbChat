# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном случае
# результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль
# tabulate). Таблица должна состоять из двух колонок
from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab(ip_addr, rng):
    results = (host_range_ping(ip_addr, rng))
    print(tabulate(results, headers='keys', tablefmt='pipe'))


if __name__ == '__main__':
    host_range_ping_tab('127.0.0.251', 5)

"""
| Reachable   | Unreachable   |
|:------------|:--------------|
| 127.0.0.251 | 127.0.0.256   |
| 127.0.0.252 |               |
| 127.0.0.253 |               |
| 127.0.0.254 |               |
| 127.0.0.255 |               |
"""
