import binascii
import hashlib
import json
import sys
import uuid
from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QTableWidget, QDialog, QLabel, QLineEdit, QPushButton, \
    QSpinBox, QFileDialog, QApplication, QTableView, QVBoxLayout, QWidget, QInputDialog, QDialogButtonBox, QFormLayout, \
    QMessageBox
from PyQt5 import QtGui

from settings import DEFAULT_IP, DEFAULT_SERVER_PORT, SERVER_DB_FILE, SALT


class RefistrationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

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

    def getInputs(self):  # возвращает кортеж
        return self.name_field.text(), self.info.text(), self.passw_field.text(), self.passw_rep.text()


# основное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(qApp.quit)

        # Основная таблица
        self.table = self.online_clients

        # Размер GUI
        self.setFixedSize(1200, 900)
        self.setWindowTitle('My first GUI - SERVER')

        # Действия
        self.just_button = QAction('Первая кнопка', self)
        self.all_clients = QAction('Клиенты Онлайн', self)
        self.online = QAction('История Клиентов(онлайн)', self)
        self.reg_form = QAction('Регистрация клиента', self)

        # объекты тулбара
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.just_button)
        self.toolbar.addAction(self.all_clients)
        self.toolbar.addAction(self.online)
        self.toolbar.addAction(self.reg_form)
        self.toolbar.addAction(exit_action)

        self.statusBar()

        # основная таблица для отображения данных
        self.main_table = QTableView(self)
        self.main_table.move(50, 100)
        self.main_table.setFixedSize(1000, 700)

        # Текст в окне - заголовок информации
        self.label = QLabel('TEXT IN WINDOW', self)
        self.label.move(50, 10)
        self.label.setFixedSize(900, 150)

        self.show()

    def online_clients(self, db):  # метод для отображения таблицы с онлайн-клиентами
        self.table = self.online_clients  # при вызове метода меняем основную таблицу
        users_list = db.get_online()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['username', 'data'])
        for login in users_list:
            result = db.get_history(login=login[0], last_entry=True)
            username = result[0]
            username = QtGui.QStandardItem(username)
            data = str(result[1])
            data = QtGui.QStandardItem(data)
            arr.appendRow([username, data])
        self.label.setText('ONLINE CLIENTS')
        self.show_table(arr)

    def history_table(self, db):  # метод для отображения таблицы с историей переписки
        self.table = self.history_table  # при вызове метода меняем основную таблицу
        result = db.messages_history()
        arr = QtGui.QStandardItemModel()
        arr.setHorizontalHeaderLabels(['author', 'recipient', 'text', 'datetime'])
        for el in result:
            author, recipient, text, time = el
            username = QtGui.QStandardItem(author)
            recipient = QtGui.QStandardItem(recipient)
            text = QtGui.QStandardItem(text)
            time = QtGui.QStandardItem(str(time))
            arr.appendRow([username, recipient, text, time])
        self.label.setText('MESSAGES HISTORY')
        self.show_table(arr)

    def show_table(self, content):
        self.main_table.setModel(content)
        self.main_table.resizeColumnsToContents()
        self.main_table.resizeRowsToContents()

    def registration(self, db):
        dialog = RefistrationForm()
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QMessageBox.Critical)
        if dialog.exec():
            name, info, passw1, passw2 = dialog.getInputs()

            if name == '' or name == None:
                msg_box.setText("Error in name field (5-10 symb)")
                msg_box.setInformativeText('Field "name" is empty!')
                msg_box.exec_()
                self.registration(db)

            elif len(name) < 5 or len(name) > 10:
                msg_box.setText("Error in name field (5-10 symb)")
                msg_box.setInformativeText('Name too short or too long')
                msg_box.exec_()
                self.registration(db)

            elif passw1 != passw2:
                msg_box.setText("Error in password logic")
                msg_box.setInformativeText("Passwords don't match")
                msg_box.exec_()
                self.registration(db)

            else:
                password = passw1.encode('utf-8')
                salt = passw1 + SALT
                salt = salt.encode('utf-8')
                key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
                db.registration_from_server(login=name, info=info, online=False, contacts=None, password=str(binascii.hexlify(key)))
                del name, info, passw1, passw2, key, salt, password

                # new_user = {name: str(key)}
                # try:
                #     with open('server_users.json', 'r') as f_r:
                #         data = json.load(f_r)
                #
                #     with open('server_users.json', 'w', encoding='utf-8') as f_w:
                #         users = data['users']
                #         users.append(new_user)
                #         json.dump(data, f_w, indent=4, ensure_ascii=False)
                # except Exception as e:
                #     print('Some error in registration', e)

# окно настроек сервера
class ConfigWindow(QDialog):
    def __init__(self, config):
        super().__init__()
        # установка основного окна
        self.setWindowTitle('Server Settings')
        self.setFixedSize(600, 400)
        # название заголовка открытия директории
        self.db_path_label = QLabel('Files Chat Project Path', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.adjustSize()
        # строка для пути расположения базы данных
        self.db_path_text = QLineEdit(self)
        self.db_path_text.move(10, 30)
        self.db_path_text.setFixedSize(290, 50)
        self.db_path_text.setReadOnly(True)
        # кнопка открытия папки
        self.db_path_button = QPushButton('Path...', self)
        self.db_path_button.move(305, 30)
        self.db_path_button.setFixedSize(85, 20)
        self.db_path_button.clicked.connect(self.open_file_window)
        # заголовок для названия базы данных
        self.db_name = QLabel('Server Database name (copy path if you need)', self)
        self.db_name.move(10, 100)
        self.db_name.adjustSize()
        # названия файла базы данных, к которой будет подключаться сервер
        self.db_text = QLineEdit(self)
        self.db_text.move(10, 150)
        self.db_text.setFixedSize(380, 20)
        # заголовок для ввода адреса ip
        self.addr_label = QLabel('addr', self)
        self.addr_label.move(10, 230)
        self.addr_label.adjustSize()
        # заголовок для ввода значения port
        self.port_label = QLabel('Port', self)
        self.port_label.move(400, 230)
        self.port_label.adjustSize()
        # поле ввода для адреса ip
        self.addr = QLineEdit(self)
        self.addr.move(10, 250)
        self.addr.setFixedSize(300, 20)
        # поле ввода для port
        self.port = QSpinBox(self)
        self.port.move(400, 250)
        self.port.setFixedSize(90, 20)
        self.port.setRange(1025, 65535)
        # кнопка подтверждения ввода настроек
        self.ok_button = QPushButton('OK', self)
        self.ok_button.move(200, 350)
        # кнопка отмены. При отмене сервер запустится с дефолтными настройками
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.move(400, 350)
        self.cancel_button.clicked.connect(self.close)
        # установка дефолтных настроек
        self.set_setting(config)
        # запуск окна
        self.show()

    def set_setting(self, config):
        addr = config.get('addr', DEFAULT_IP)
        port = config.get('port', DEFAULT_SERVER_PORT)
        db_name = config.get('db_name', SERVER_DB_FILE)
        self.addr.setText(addr)
        self.port.setValue(port)
        self.db_text.setText(db_name)

    def setting_dict(self):
        return {
            'addr': self.addr.text(),
            'port': self.port.value(),
            'db_name': self.db_text.text(),
        }

    def open_file_window(self):
        file_dialog = QFileDialog(self)
        path = file_dialog.getExistingDirectory()
        self.db_path_text.setText(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    conf = ConfigWindow({})
    app.exec_()
