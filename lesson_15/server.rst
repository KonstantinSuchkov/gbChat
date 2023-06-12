server.py
==========

Серверная часть чата.
Запуск - python server.py
Дополнительные параметры при запуске:
- -a addr, IP, default='localhost'
- -p port, default=7777
Пример запуска: python server.py -p 8888 - запуск со значением addr = localhost, IP = 8888



class ServerPort:
    # дескриптор, не позволяет основному классу запускать сервер с неправильным параметром порта

    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            raise ValueError(f'Wrong port: {value}')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name



class ServerVerifier(type):
    # метакласс, запрет 'accept', 'listen'


class Server(threading.Thread, metaclass=ServerVerifier):
    """Основной класс серверной части чата.
    """
    port = ServerPort()  # инициализация класса-дескриптора для проверки и установки значения порта

    @staticmethod
    def create_socket_server(addr, port):
        """ функция создания сокета сервера
        :params: server port and address
        :return: s:socket
        """


    def read_requests(self, r_clients, all_clients, users):
        """ Чтение запросов из списка клиентов
        :params: clients (get from select)
        :return: dict {socket: data} # Словарь ответов сервера вида {сокет: запрос}
        """
    @log
    def presence_answer(self, d):
        """ формирование ответа клиенту на presense сообщение
        :params: dict
        :return: message bytes
        """

    def write_responses(self, requests, w_clients, clients, chat, users):
        """ Ответ сервера клиентам. Распоковка приходящих данных от клиентов, раскодировка.
        Получение инструкций и отправка сообщений клиентам.
        :params: clients requests, clients, chat(list of messages)
        result: send message to clients
        """

    @log
    def send_data(self, data, sock):
        """функция отправки данных
        :param sock: socket
        :param data: dict
        """

    def main(self):
        """ Основной метод класса с серверной логикой чата. Проверка подключений.
        Проверка наличия событий ввода-вывода. Сохранение запросов клиентов, отправка ответов клиентам
        """

    def admin_commands(self):
    # функция для администрирования серверной части чата, ввода команд
       'exit', 'online', 'h'(history)

# вспомогательная функция

def get_addr_port():
    """ получение (парсинг) аргументов
    -a -> addr
    -p -> port
    :return ArgumentParser()
    """

# GUI Functions
def refresh_table():
    main_window.table(db=server.db)

def all_clients(db):

def on_line(db):

def save_config(config_window):

if __name__ == '__main__':
    # сначала запускаем окно настроек
    # полученные из ConfigWindow настройки в файл
    # полученные из ConfigWindow настройки передаем в файл
    # запуск сервера через командную строку
    # server = Server(*get_addr_port())
    # после получения настроек используем их для запуска сервера
    # запуск сервера через приложение
    # запускаем первый поток с основным методом класса Server
    # определяем второй поток для возможности ввода команд
    # таймер для обновления отображения данных в приложении

    server.admin_commands()

==========