# Form implementation generated from reading ui file 'Login.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
import json
from globalVars import globalVars
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QLineEdit, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from client import *
import config
import os


class Login(QtWidgets.QWidget):
    switch_window_register = QtCore.pyqtSignal()
    switch_window_login = QtCore.pyqtSignal()
    loginClient = client()

    def __init__(self):
        super(Login, self).__init__()
        self.ui = uic.loadUi("Login.ui")
        self.ui.pushButton.clicked.connect(self.registerClicked)
        self.ui.pushButton_2.clicked.connect(self.loginClicked)
        self.ui.lineEdit.setPlaceholderText("账号")
        self.ui.lineEdit_2.setPlaceholderText("密码")
        self.ui.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
        pixmap = QPixmap("logo_v.png")  # 按指定路径找到图片
        self.ui.label.setPixmap(pixmap)  # 在label上显示图片
        self.ui.label.setScaledContents(True)  # 让图片自适应label大小

    def loginClicked(self):
        user_name = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        print("登陆", user_name, password)
        ans = self.loginClient.login(user_name, password)
        print(ans)
        if ans['statusCode'] == 200:
            # print(cookie)
            QMessageBox.about(self, '', '登陆成功')
            config.set_current_user(user_name)
            user_config = config.get_user_config(user_name)
            if user_config is None:
                user_config = {'upload_index': 0, 'upload_list': {}, 'download_index': 0, 'download_list': {}}
            user_config['Cookie'] = self.loginClient.headers['Cookie']
            config.set_user_config(user_name, user_config)
            self.ui.close()
            self.switch_window_login.emit()

        # if res.status_code == 200:
        #     ret = json.loads(res.text)
        #     print(ret['message'])
        #     if ret['message'] == 'success':
        #         # global cookie
        #         cookie = res.headers["Set-Cookie"]
        #         print(cookie)
        #         # gv.clearAllVars()
        #         # gv.setVar({'cookie': cookie})
        #         QMessageBox.about(self, '', '登陆成功')
        #         self.ui.close()
        #         self.switch_window_login.emit()
        #     else:
        #         QMessageBox.critical(self,'',ret['message'])
        # else:
        #     print(self.text)
        # QMessageBox.critical(self,'登陆失败')

    def registerClicked(self):
        self.ui.close()
        self.switch_window_register.emit()
