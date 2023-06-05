import sys

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QLineEdit, QPushButton, \
    QApplication, QTableView, QInputDialog, QListWidget, QVBoxLayout, QDialog, QDialogButtonBox, QFormLayout
from PyQt5 import QtGui, Qt


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.name_field = QLineEdit(self)
        self.info = QLineEdit(self)
        self.passw_field = QLineEdit(self)
        self.passw_rep = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Client login/name", self.name_field)
        layout.addRow("Client info / status", self.info)
        layout.addRow("Client password", self.passw_field)
        layout.addRow("Repeat password", self.passw_rep)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.show()

    def getInputs(self):  # возвращает кортеж
        return self.name_field.text(), self.info.text(), self.passw_field.text(), self.passw_rep.text()


class Widget(Qt.QWidget):  # отображение клиентов для отправки писем только одному клиенту
    # def __init__(self, parent = None):
    #     super(Widget, self).__init__(parent)

    def __init__(self):
        super().__init__()


# основное окно приложения
class MainClientWindow(QMainWindow):
    valueChanged = pyqtSignal(str)
    valueDelChanged = pyqtSignal(str)

    sendChanged = pyqtSignal(int)
    sendOne = pyqtSignal(int)

    def __init__(self, user):
        self.user = user
        self.timer = QTimer()
        self.contact_arr = []

        super().__init__()
        self.initUI()

    def initUI(self):

        self.contact = ''
        self.message_count = 0
        self.listWidget = None
        self.listWidget11 = None
        self.message = ''
        # self.chat_arr = []

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(qApp.quit)

        # Основная таблица
        self.table = self.contact_list

        # Размер GUI
        self.setFixedSize(1200, 900)
        self.setWindowTitle(f'My first GUI - CLIENT {self.user}')

        # Действия
        self.get_online = QAction('Обновить Онлайн', self)
        self.all_clients = QAction('Ваш Список контактов', self)
        self.history = QAction('История сообщений', self)
        self.chat_table = QAction('Начать чат', self)

        # объекты тулбара
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.get_online)
        self.toolbar.addAction(self.all_clients)
        self.toolbar.addAction(self.history)
        self.toolbar.addAction(self.chat_table)
        self.toolbar.addAction(exit_action)

        self.statusBar()

        # Список клиентов, работает(кликабелен) только последний элемент
        # self.listWidget11 = QListWidget(self)
        # self.listWidget11.move(600, 120)
        # self.listWidget11.setFixedSize(500, 720)
        # self.listWidget11.setSelectionMode(2)

        # основная таблица для отображения данных
        self.main_table = QTableView(self)
        self.main_table.move(50, 120)
        self.main_table.setFixedSize(500, 720)

        # Текст в окне - заголовок информации
        self.label = QLabel('TEXT IN WINDOW', self)
        self.label.move(50, 30)
        self.label.setFixedSize(900, 150)

        # Текст в окне - инструкция
        self.instuction = QLabel(' 1. Нажать на "Обновить Онлайн"\n 2. Нажать на "Ваш список контактов"\n Заполнить '
                                 'окно текста и нажать "кнопку отправить"\n Сообщение будет отправлено всем клиентам,'
                                 '\n удовлетваряющим требованиям:\n 1) Клиент онлайн\n 2) Клиент в списке контактов\n '
                                 'Для отправки только одному клиенту:\n Написать текст сообщения\n Двойное нажатие на '
                                 'список контактов\n Двойное нажатие мышью на имени адресата\n "Вывести чат" - '
                                 'отображение сообщений', self)
        self.instuction.move(600, 100)
        self.instuction.setFixedSize(400, 250)

        # кнопка добавить контакт
        self.add_contact = QPushButton('ДОБАВИТЬ КОНТАКТ', self)
        self.add_contact.move(170, 25)
        self.add_contact.setFixedSize(170, 40)
        self.add_contact.clicked.connect(self.showAddDialog)
        # кнопка удалить контакт
        self.del_contact = QPushButton('УДАЛИТЬ КОНТАКТ', self)
        self.del_contact.move(170, 55)
        self.del_contact.setFixedSize(170, 40)
        self.del_contact.clicked.connect(self.showDelDialog)

        # кнопка отправить сообщение
        self.send_text = QPushButton('ОТПРАВИТЬ', self)
        self.send_text.move(920, 60)
        self.send_text.setFixedSize(170, 40)
        self.send_text.clicked.connect(self.message_signal)
        # поле ввода текста
        self.text = QLineEdit(self)
        self.text.move(610, 60)
        self.text.setFixedSize(300, 30)

        # self.listWidget11.itemDoubleClicked.connect(self.send_to_one)
        self.main_table.doubleClicked.connect(self.on_doubleclick)

        self.show()

    def on_doubleclick(self):
        self.start()

    def send_to_one(self, item):  # обработка сигнала при отправке сообщения одному получателя при нажатии мыши
        print('item clicked', item.text())
        self.contact = item.text()
        self.sendOne.emit(+1)
        self.text.setText('')

    def start(self):  # отображение списка клиентов, для отправки ссобщений каждому клиенту по щелчку мыши

        # Вариант ListWidget в главном окне, но так у меня работает(кликабельный) только последний объект
        items = []
        # for x in range(self.listWidget11.count() - 1):
        #     items.append(self.listWidget11.item(x).text())
        # self.listWidget11.clear()
        # print('1 items', items)
        # print('2 contact_arr', list(set(self.contact_arr)))
        # self.listWidget11.addItems(items)

        global m  # Вариант ListWidget в отдельном окне
        m = Widget()
        listWidget = QListWidget()
        listWidget.setWindowTitle("Send to One")
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(listWidget)
        m.setLayout(window_layout)
        listWidget.addItems(list(set(self.contact_arr)))
        listWidget.itemDoubleClicked.connect(self.send_to_one)  # при двойном нажатии на имя - отправка кдиенту
        m.show()

    def contact_list(self, db, online, chat_arr):  # метод для отображения таблицы с онлайн-клиентами
        self.table = self.contact_list  # при вызове метода меняем основную таблицу
        contacts = db.get_contacts()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['contacts'])
        for login in contacts:
            login = str(login)
            self.contact_arr = list(set(self.contact_arr))
            if login not in self.contact_arr:
                self.contact_arr.append(login)
            login = QtGui.QStandardItem(login)
            arr.appendRow([login])
        self.label.setText('YOUR CONTACTS')
        self.show_table(arr)

    def history_table(self, db, online, chat_arr):  # метод для отображения таблицы с историей переписки
        self.table = self.history_table  # при вызове метода меняем основную таблицу
        result = db.get_history()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['recipient', 'text', 'datetime'])
        for el in result:
            recipient, text, time = el
            recipient = QtGui.QStandardItem(recipient)
            text = QtGui.QStandardItem(text)
            time = QtGui.QStandardItem(str(time))
            arr.appendRow([recipient, text, time])
        self.label.setText('MESSAGES HISTORY')
        self.show_table(arr)

    def write_online(self, db, online, chat_arr):
        self.table = self.write_online  # при вызове метода меняем основную таблицу
        online = online
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['online'])
        for login in online:
            login = str(login)
            login = QtGui.QStandardItem(login)
            arr.appendRow([login])
        self.label.setText('ONLINE')
        self.show_table(arr)

    def write_chat(self, db, online, chat_arr):  # отображение чата (входящие и исходящие сообщения)
        self.table = self.write_chat  # при вызове метода меняем основную таблицу
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['messages'])
        for message in chat_arr:
            message = str(message)
            message = QtGui.QStandardItem(message)
            arr.appendRow([message])
        self.label.setText('CHAT')
        self.show_table(arr)

    def showAddDialog(self):  # диалог добавления нового контакта
        text, ok = QInputDialog.getText(self, 'update contact', 'enter nickname to add in contacts list:')
        if ok:
            self.contact = (str(text))
            self.on_changed_value(self.contact)

    def showDelDialog(self):  # диалог удаления контакта
        text, ok = QInputDialog.getText(self, 'delete contact', 'enter nickname to delete in contacts list:')
        if ok:
            self.contact = (str(text))
            self.valueDelChanged.emit(self.contact)  # активируем сигнал

    def on_changed_value(self, value):  # сигнал, для добавления контакта, client.py ожидает сигнала для выполнения
        self.valueChanged.emit(value)  # инструкций по добавлению контактов в клиентскую базу данных.

    def return_new_contact(self):  # передача в client.py контакта-получателя
        return self.contact

    def message_signal(self):  # сигнал, для client.py для отправки сообщения
        self.sendChanged.emit(+1)
        self.sleep1sec()  # кнопка отключится на 1 секунду для защиты от спама
        self.text.setText('')

    def show_message(self):  # передача сообщения в client.py
        self.message = self.text.text()
        print(self.message)  # отображение сообщения в терминале
        return self.message

    def show_message_to_one(self):  # передача сообщения в client.py
        self.message = [self.text.text(), [self.contact]]  # при отправке одному клиенту сообщение будет иметь
        print(self.message[0])  # тип "список", вторым элементом которого будет никнейм получателя сообщения
        return self.message

    def show_table(self, content):  # метод отображения таблицы в основном окне
        self.main_table.setModel(content)
        self.main_table.resizeColumnsToContents()
        self.main_table.resizeRowsToContents()

    def sleep1sec(self):  # антиспам защита
        self.send_text.setEnabled(False)
        QTimer.singleShot(1000, lambda: self.send_text.setDisabled(False))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AuthWindow()
    # conf = MainClientWindow(user='Amelia')
    if window.exec():
        print(window.name_field.text())
        print('info=', type(window.info.text()))
    # app.exec_()
    # exit(0)

