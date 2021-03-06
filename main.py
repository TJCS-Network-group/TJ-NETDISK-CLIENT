#!/usr/bin/python
import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from LoginWindow import Login
from RegisterWindow import Register
from NetDiskWindow import NetDisk
import config
from client import client
cookie = None

class Controller:

    def __init__(self):
        self.window = None

    def show_login(self):
        print(self.window)
        self.window = Login()
        self.window.switch_window_login.connect(self.show_netdisk)
        self.window.switch_window_register.connect(self.show_register)
        self.window.ui.show()

    def show_register(self):
        print("register")
        self.window = Register()
        self.window.switch_window_login.connect(self.show_login)
        self.window.ui.show()

    def show_netdisk(self):
        print("main")
        self.window = NetDisk()
        self.window.switch_window_login.connect(self.show_login)

        # self.window = QMainWindow()
        # self.window.switch_window.connect(self.show_window_two)
        # self.login.close()
        # self.window.show()




def main():
    app = QApplication(sys.argv)
    controller = Controller()
    config._init()

    current_user = config.get_current_user()
    user_config = config.get_user_config(current_user)
    if user_config is None or user_config['Cookie'] is None:
        controller.show_login()
    else:
        client_t = client()
        client_t.headers['Cookie'] = user_config['Cookie']
        ans = client_t.get_identity()
        print(ans)
        if ans['data']['login']:
            controller.show_netdisk()
        else:
            controller.show_login()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

# import sys
# from PyQt6 import QtCore, QtWidgets
#
#
# class MainWindow(QtWidgets.QWidget):
#
#     switch_window = QtCore.pyqtSignal(str)
#
#     def __init__(self):
#         QtWidgets.QWidget.__init__(self)
#         self.setWindowTitle('Main Window')
#
#         layout = QtWidgets.QGridLayout()
#
#         self.line_edit = QtWidgets.QLineEdit()
#         layout.addWidget(self.line_edit)
#
#         self.button = QtWidgets.QPushButton('Switch Window')
#         self.button.clicked.connect(self.switch)
#         layout.addWidget(self.button)
#
#         self.setLayout(layout)
#
#     def switch(self):
#         self.switch_window.emit(self.line_edit.text())
#
#
# class WindowTwo(QtWidgets.QWidget):
#
#     def __init__(self, text):
#         QtWidgets.QWidget.__init__(self)
#         self.setWindowTitle('Window Two')
#
#         layout = QtWidgets.QGridLayout()
#
#         self.label = QtWidgets.QLabel(text)
#         layout.addWidget(self.label)
#
#         self.button = QtWidgets.QPushButton('Close')
#         self.button.clicked.connect(self.close)
#
#         layout.addWidget(self.button)
#
#         self.setLayout(layout)
#
#
# class Login(QtWidgets.QWidget):
#
#     switch_window = QtCore.pyqtSignal()
#
#     def __init__(self):
#         QtWidgets.QWidget.__init__(self)
#         self.setWindowTitle('Login')
#
#         layout = QtWidgets.QGridLayout()
#
#         self.button = QtWidgets.QPushButton('Login')
#         self.button.clicked.connect(self.login)
#
#         layout.addWidget(self.button)
#
#         self.setLayout(layout)
#
#     def login(self):
#         self.switch_window.emit()
#
#
# class Controller:
#
#     def __init__(self):
#         pass
#
#     def show_login(self):
#         self.login = Login()
#         self.login.switch_window.connect(self.show_main)
#         self.login.show()
#
#     def show_main(self):
#         self.window = MainWindow()
#         self.window.switch_window.connect(self.show_window_two)
#         self.login.close()
#         self.window.show()
#
#     def show_window_two(self, text):
#         self.window_two = WindowTwo(text)
#         self.window.close()
#         self.window_two.show()
#
#
# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     controller = Controller()
#     controller.show_login()
#     sys.exit(app.exec())
#
#
# if __name__ == '__main__':
#     main()
