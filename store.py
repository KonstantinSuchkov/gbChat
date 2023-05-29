import datetime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, registry
from settings import SERVER_DB_FILE

# lesson 12
# b) Реализовать хранение информации в БД на стороне клиента:
# * список контактов;
# * история сообщений.
# класс БД для клиента


class StoreClient:
    class Contacts:  # простой класс, который будет содержать контакты клиента
        def __init__(self, client):
            self.id = None
            self.client = client

        def __repr__(self):
            return self.client

    class History:  # класс истории сообщений клиента
        def __init__(self, recipient, text):
            self.id = None
            self.recipient = recipient
            self.text = text
            self.time = datetime.datetime.now()

        def __repr__(self):
            return "<Message('recipient:%s', 'text:%s', 'time:%s')>" % (self.recipient, self.text, self.time)

    def __init__(self, client):
        self.client = client
        self.db_engine = create_engine(f'sqlite:///db/{client}_db.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        contacts_table = Table('Contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('client', String)
                               )

        history_table = Table('History', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('recipient', String(96)),
                              Column('text', String(1024)),
                              Column('time', DateTime)
                              )

        self.metadata.create_all(self.db_engine)
        mapper_registry = registry()  # в версии sqlalchemy 2.0+ используется registry map_imperatively, а не mapper
        mapper_registry.map_imperatively(self.Contacts, contacts_table)
        mapper_registry.map_imperatively(self.History, history_table)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.commit()

    def get_contacts(self):
        return self.session.query(self.Contacts).all()

    def add_contact(self, contact):
        new_rec = self.Contacts(client=contact)
        exists = self.session.query(self.Contacts).filter_by(client=contact).first() is not None
        if exists:
            print(f'contact {contact} already in Table contacts')
        else:
            self.session.add(new_rec)
            self.session.commit()

    def del_contacts(self, contact):
        exists = self.session.query(self.Contacts).filter_by(client=contact).first() is not None
        if exists:
            del_rec = self.session.query(self.Contacts).filter_by(client=contact).first()
            self.session.delete(del_rec)
            self.session.commit()
        else:
            print(f'contact {contact} not in Table contacts. Cant deleting')

    def add_history(self, recipient, text):
        history_rec = self.History(recipient=recipient, text=text)
        self.session.add(history_rec)
        self.session.commit()

    def get_history(self):
        return self.session.query(self.History).all()


#####################################
# класс БД для сервера
class StoreServer:
    class User:

        login = None

        # online = False

        def __init__(self, login, info, online, contacts):
            self.id = None
            self.login = login
            self.info = info
            self.online = online
            self.contacts = contacts

        def __repr__(self):
            return self.login

    class History:

        def __init__(self, clients_id, entry_time, ip):
            self.id = None
            self.clients_id = clients_id
            self.entry_time = entry_time
            self.ip = ip

        def __repr__(self):
            return "('id:%s', 'время входа:%s', 'ip:%s')" % (self.clients_id, self.entry_time, self.ip)

    class MessageHistory:  # класс истории сообщений клиентов
        def __init__(self, author, recipient, text):
            self.id = None
            self.author = author
            self.recipient = recipient
            self.text = text
            self.time = datetime.datetime.now()

        def __iter__(self):
            yield self.author
            yield self.recipient
            yield self.text
            yield self.time

    class ContactList:

        def __init__(self, owner_id, contacts):
            self.id = None
            self.owner_id = owner_id
            self.contacts = contacts

        def __repr__(self):
            return f"user {self.owner_id}: {self.contacts}"

    def __init__(self, db_name):
        self.db_engine = create_engine(f'sqlite:///{db_name}', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        clients = Table('clients', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('login', String),
                        Column('info', String),
                        Column('online', Boolean, default=False),
                        Column('contacts', String, default=None)
                        )

        clients_history = Table('history', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('clients_id', ForeignKey('clients.id')),
                                Column('entry_time', DateTime),
                                Column('ip', String)
                                )

        contacts_list = Table('contacts_list', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('contacts', String),
                              Column('owner_id', Integer, ForeignKey('clients.id')),
                              )

        message_history = Table('messages', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('author', String(96)),
                                Column('recipient', String(96)),
                                Column('text', String(1024)),
                                Column('time', DateTime)
                                )

        self.metadata.create_all(self.db_engine)
        mapper_registry = registry()  # в версии sqlalchemy 2.0+ используется registry map_imperatively, а не mapper
        mapper_registry.map_imperatively(self.User, clients)
        mapper_registry.map_imperatively(self.History, clients_history)
        mapper_registry.map_imperatively(self.ContactList, contacts_list)
        mapper_registry.map_imperatively(self.MessageHistory, message_history)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.commit()

    def client_login(self, login, info, ip, online, contacts):
        result = self.session.query(self.User).filter_by(login=login)
        if result.count():
            user = result.first()
            user.online = True
        else:
            user = self.User(login, info, online, contacts)
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
        result = ', '.join(str(x) for x in clients.all())
        return result

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
                history = history[-1]
            return history
        return history.all()

    def add_contact(self, login, contact):
        client = self.session.query(self.User).filter(self.User.login == login)
        if client[0].contacts == None or client[0].contacts == '':  # если это контакт, то значение None
            client[0].contacts = contact  # тогда просто добавляем новый контакт
        else:  # иначе
            res = client[0].contacts  # запоминаем предыдущие контакты
            contacts = self.get_contacts(login)  # создаем список контактов
            if contact not in contacts:  # если контакта еще нет в списке контактов
                client[0].contacts = res + ',' + contact  # то добавляем новый контакт к старым
            else:
                print(f'Contact {contact} already in contacts')
        self.session.commit()

    def get_contacts(self, login):
        client = self.session.query(self.User).filter(self.User.login == login)
        try:
            contacts = client[0].contacts.split(',')
            return [contact for contact in contacts]
        except AttributeError:
            return ['']

    def del_contacts(self, login, contact):
        contacts = self.get_contacts(login)  # создаем список контактов
        client = self.session.query(self.User).filter(self.User.login == login)
        if contact in contacts:  # если контакта еще нет в списке контактов, то добавим его
            for el in contacts:
                if el == contact:
                    contacts.remove(el)
                    contacts = ','.join(contacts)
                    client[0].contacts = contacts
                    self.session.commit()
        else:
            print(f'Not contact {contact} in contacts, cant to delete')

    def messages_history(self):
        history = self.session.query(self.MessageHistory)
        return history.all()


# testing
if __name__ == '__main__':
    db = StoreServer(SERVER_DB_FILE)
    # history_rec = db.MessageHistory(author='Test1', recipient='Test2', text='test text')
    # db.session.add(history_rec)
    # db.session.commit()
    # print(db.get_messages_history())
    # # db.client_login('user_1', 'test_user', '7777', online=True, contacts='')
    # # db.client_login('user_4', 'test_user', '7777', online=False)
    # print(db.get_clients())
    # print(db.get_online())
    # print(db.client_disconnect(login='Test1'))
    # print(db.add_contact('Varvara', 'Admin'))
    # db.add_contact('Amelia', 'Жанна')
    # db.add_contact('Varvara', 'Жанна')
    # # print(db.get_contacts('Test1'))
    # db.del_contacts('Varvara', 'Admin')
    # print(db.get_contacts('Varvara'))
    # print(db.get_contacts('Varvara'))
    # # print(db.get_contacts('Test1'))
    # # print(db.get_contacts('Varvara'))
    # print(db.get_history(login='Amelia', last_entry=True))
    # print(db.get_history())
    print(db.messages_history())

    # db_client = StoreClient('Amelia')
    # # db_client.add_contact('Admin')
    # # db_client.del_contacts('Papa')
    # # print(db_client.get_contacts())
    # db_client.add_history(recipient='Varvara', text='Hello, Amelia!')
    # print(db_client.get_history())
