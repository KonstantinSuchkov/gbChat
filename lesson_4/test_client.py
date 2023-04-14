import json
import unittest
from lesson_3.client import presence, get_addr_port, read_answer


# тестовые данные
test_data = {
    "action": "presence",
    "time": 1.123,
    "type": "status",
    "user": {
        "account_name": 'account_name',
        "status": 'status'
    }
}


# функция для теста обработки сообщений от сервера
def for_test_msg_to_client(d):
    if d['action'] == 'presence':
        msg = {
            "response": 200,
            "time": 1.123,
            "alert": "Code 200!!! Code 200"
        }
        msg = json.dumps(msg, indent=4).encode('utf-8')
        # client.send(msg) - отключаем client.send, чтобы не поймать ошибку соединения
        return msg


# тесты для client.py - lesson_3
class TestClient(unittest.TestCase):
    def test_presence(self):
        test_result = presence(account_name='account_name', status='status')  # вызываем функцию presence
        test_result['time'] = 1.123  # принудительно поменяем штамп time
        self.assertEqual(test_result, test_data)  # ожидаем получить тестовые данные

    def test_get_addr_port(self):
        self.assertEqual(str(get_addr_port()), "Namespace(addr='localhost', port=7777, user='Varvara', status='2 "
                                               "years')")  # при вызове функции get_addr_port()
        # ожидаем дефолтные значения адреса и порта

    def test_read_answer(self):
        test_result = json.loads(for_test_msg_to_client(test_data))  # вызываем тестовую функцию и преобразовываем
        # результат в словарь (т.к. client.send(msg) отключен) - имитируем отправку ответа сервера
        expected_output = read_answer(test_result)  # вызываем функцию чтения ответа от сервера
        actual_result = (200, 'Code 200!!! Code 200')  # ожидаемый результат
        self.assertEqual(expected_output, actual_result)


if __name__ == "__main__":
    unittest.main()

# Ran 3 tests in 0.004s
# OK
# Process finished with exit code 0
