import re
import unittest
from datetime import datetime
from lesson_3.server import create_socket_server, msg_to_client, get_addr_port

# тестовые данные
test_data = {
    "action": "NO-PRESENCE_ACTION",  # "неправильный" action
    "time": datetime.timestamp(datetime.now()),
    "type": "status",
    "user": {
        "account_name": 'account_name',
        "status": 'status'
    }
}


# тесты для server.py - lesson_3
class TestServer(unittest.TestCase):
    def test_create_socket_server(self):
        search_point = re.search("laddr=(.*)>", str(create_socket_server('', 7777)))
        self.assertEqual(search_point.group(), "laddr=('0.0.0.0', 7777)>")  # создаем дефолтный сокет, ожидаем
        # laddr=('0.0.0.0', 7777)>

    def test_msg_to_client(self):
        self.assertEqual(msg_to_client(test_data, client='test_client'), None)  # передаем в функцию данные с
        # неправильным action, ожидаем None

    def test_get_addr_port(self):
        self.assertEqual(str(get_addr_port()), "Namespace(addr='', port=7777)")  # при вызове функции get_addr_port()
        # ожидаем дефолтные значения адреса и порта

    def test_get_another_port(self):
        parsed = get_addr_port()
        parsed.port = '8888'
        self.assertEqual(str(parsed.port), '8888')


if __name__ == "__main__":
    unittest.main()

# Ran 4 tests in 0.014s
#
# OK
