import datetime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean, update
from sqlalchemy.orm import sessionmaker, registry


# Задание 11 1. Начать реализацию класса «Хранилище» для серверной стороны. Хранение необходимо осуществлять в базе
# данных. В качестве СУБД использовать sqlite. Для взаимодействия с БД можно применять ORM. Опорная схема базы
# данных: На стороне сервера БД содержит следующие таблицы: a) клиент: * логин; * информация. b) история клиента: *
# время входа; * ip-адрес. c) список контактов (составляется на основании выборки всех записей с id_владельца): *
# id_владельца; * id_клиента.


class StoreServer:
    class User:

        login = None

        # online = False

        def __init__(self, login, info, online):
            self.id = None
            self.login = login
            self.info = info
            self.online = online

        def __repr__(self):
            return "<User('login:%s','info/status:%s', 'online:%s')>" % (self.login, self.info, self.online)

    class History:

        def __init__(self, clients_id, entry_time, ip):
            self.id = None
            self.clients_id = clients_id
            self.entry_time = entry_time
            self.ip = ip

        def __repr__(self):
            return "<History('id:%s','время входа:%s', 'ip:%s')>" % (self.clients_id, self.entry_time, self.ip)

    class ContactList:

        def __init__(self, users_id):
            self.id = None
            self.users_id = users_id

        def __repr__(self):
            return "<Contacts('%s')>" % self.users_id

    def __init__(self):
        self.db_engine = create_engine('sqlite:///server_db.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        clients = Table('clients', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('login', String),
                        Column('info', String),
                        Column('online', Boolean, default=False),
                        )

        clients_history = Table('history', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('clients_id', ForeignKey('clients.id')),
                                Column('entry_time', DateTime),
                                Column('ip', String), )

        contacts_list = Table('list', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('clients_id', ForeignKey('clients.id')),
                              )

        self.metadata.create_all(self.db_engine)
        mapper_registry = registry()  # в версии sqlalchemy 2.0+ используется registry, а не mapper
        mapper_registry.map_imperatively(self.User, clients)
        mapper_registry.map_imperatively(self.History, clients_history)
        mapper_registry.map_imperatively(self.ContactList, contacts_list)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.commit()

    def client_login(self, login, info, ip, online):
        result = self.session.query(self.User).filter_by(login=login)
        if result.count():
            user = result.first()
            user.online = True
        else:
            user = self.User(login, info, online)
            self.session.add(user)
            self.session.commit()

        self.session.add(self.History(clients_id=user.id, entry_time=datetime.datetime.now(), ip=ip))
        self.session.commit()

        return user.id

    def client_disconnect(self, login):
        clients = self.session.query(self.User)
        client = clients.filter(self.User.login == login)
        if client:
            client = client.all()
            client[0].online = False
            print(client)
            self.session.commit()
            print(f'{client[0].login} - disconnecting')
        else:
            print(f'Client not found')

    def get_clients(self):
        clients = self.session.query(self.User)
        return clients.all()

    def get_online(self):
        clients = self.session.query(self.User.login)
        clients = clients.filter(self.User.online == True)
        clients = clients.all()
        return clients

    def get_history(self, login=None, last_entry=False):
        history = self.session.query(self.User.login, self.History).join(self.User)
        if login:  # по параметру login отфильтруем историю
            history = history.filter(self.User.login == login)
            history = history.all()
        if last_entry:  # если есть параметр last_entry, то отобразится только история последнего входа клиента
            if len(history) > 1:
                history = history[-1]
        return history


# testing
if __name__ == '__main__':
    db = StoreServer()
    # db.client_login('user_1', 'test_user', '7777', online=True)
    # db.client_login('user_4', 'test_user', '7777', online=False)
    print(db.get_clients())
    print(db.get_history(login='user_4', last_entry=True))
    print(db.get_online())
    print(db.client_disconnect(login='user_4'))
