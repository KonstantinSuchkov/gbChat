client.py
==========

Основное приложение клиентской части чата.
Запуск : python client.py.
Дополнительные параметры при запуске:
- -a addr, IP, default='localhost'
- -p port, default=7777
Пример запуска: python client.py -p 8888 - запуск клиента со значением addr = localhost, IP = 8888
После запуска клиенту будет предложено авторизоваться. Регистрация клиентов происходит на сервере.
После успешной авторизации откроется окно приложения для ввода сообщений.


class ClientVerifier(type):
    """
    Метакласс для контроля недопущения создания сокетов на уровне классов
    """


class Client(metaclass=ClientVerifier):
    """
    Основной класс клиента
    """

    def run(self):
        """
        Основной метод класса с логикой чата. Отправка хэша пароля для авторизации.
        Генерация пары ключей для шифрования сообщений. Отправка presence сообщения.
        Инициализация базы данных клиента, открытие приложения. Потоки на прием и отправку данных. Обработка сигналов
        """

        # Блок авторизации, создание ключей для ассиметричного шифрования
        self.send_data(self.check_password(), self.s)
        while True:
            try:
                data = self.data_from_server(self.s)
                answer = self.read_answer(data)
                print(answer)
                client_log.info(f'Message from Server received: {answer} ')

                key = RSA.generate(2048)
                self.privateKey = key.export_key()
                self.publicKey = key.publickey().export_key()

                presence_msg = self.presence(self.user, self.status, self.publicKey.decode('ascii'))  # создаем presence-сообщение
                print('Presence message sending...')
                client_log.info('Presence message sending...')
                self.send_data(presence_msg, self.s)
                client_log.info('Presence message sending...DONE')
                print('Presence message sending...DONE')
            except Exception as err:
                client_log.error(f'Some errors in authentification: {err}')
                exit(1)

            # Авторизация прошла


    def check_password(self):
        """ Функция(метод) формирует словарь для отправки на сервер и проверки правильности введненного пароля.
        Словарь содержит ключ "action" со значением "checking", по которому сервер определит назначение словаря.
        Ключ "hash" хранит хэш пароля введенного пользователем для сравнения с хэшом пароля этого же пользователя
        в серверной базе данной.
        """

    @staticmethod
    def data_from_server(sock):
        """ функция(метод) для преобразования ответа с сервера в словарь
        :params: sock: socket
        :return: dict
        """

    def read_answer(self, dict_from_server):
        """ Функция(метод) для считывания ответа из данных (словаря), поступивших с сервера.
        Полученные зашифрованные сообщения дешифровываются публичными ключами клиентов, переданных сервером.
        :params: dict
        :return str: username: {text}
        """

    def chat_r_message(self, sock):
        """ функция(метод) отображения сообщений других пользователей, для работы в режиме "многопоточности".
        Пока клиент запущен будем ожидать сообщений от других клиентов.
        Строка сообщения выводится по примеру >>>username: TEXT
        :params: sock: socket
        """


    def chat_w_message(self, user, s):
        """ функция(метод) отправки сообщений другим пользователям, для работы в режиме "многопоточности".
        Пока клиент запущен будем ожидать ввода сообщения от пользователя.
        Поддерживаемые команды:
        exit - выход
        list - список контактов
        history - история сообщений
        online - клиенты онлайн
        add - добавить клиента
        del - удалить клиента
        :params: sock: socket, user: username
        """


    @staticmethod
    def presence(account_name, status, public_key):
        """ функция(метод) для формирования presence-сообщения
        :params: account_name, status
        :return: dict
        """


    @staticmethod
    def send_data(data, sock):
        """функция(метод) отправки данных
        :param sock: socket
        :param data: dict
        """

    def message_to_server(self, message, author, receiver):
        """ функция(метод) для формирования сообщения
        :param message: str
        :param author: str
        :param receiver: str
        :return: dict
        """

    # GUI and other Functions
    def refresh_table(self):
        self.main_window.table(db=self.db, online=self.online, chat_arr=self.chat_arr)

    def main_send_message(self, message, user, s):
        # стандартный протокол отправки сообщения на сервер

    def get_online(self, user, s):
        # формируем запрос по ТЗ к серверу с action "get_contacts"

    def add_contact(self, user, contact, s):

    def del_contact(self, user, s, contact):

    def chat_table(self):
        функция отображения основного окна в приложении чата
        self.main_window.chat_table()

    def get_receivers(self):
        # список контактов клиента, получаем из клиентской БД


# основная функция включает в себя создание сокета, тк по ТЗ мы не можем создать сокет на уровне класса
def main(addr, port, user, status, password):
    """основная функция для запуска клиента чата
    :param addr: server ip
    :param port: server port
    :param user: username
    :param status: user status
    :param password: hash
    :return: client run
    """
    client_log.info('client.py start...')
    client_log.info(f'Func get_addr_port...DONE, params = {addr}, {port}, {user}, {status}')
    s = create_socket_client(addr, port)  # создаем сокет
    client = Client(s, user, status, password)  # создаем объект класса клиент с параметрами сокета, порта, адреса
    client.run()  # запускаем клиент с помощью метода run

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
def get_addr_port():
    """ функция для получения параметров из командной строки, запуска окна авторизации.
    Возврат введенных данных в окне авторизации. Пароль возвращается в виде хэша
    """
    return addr, port, user, status, hash_item
==========