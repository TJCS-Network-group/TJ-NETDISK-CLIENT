from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QLineEdit, QMenu, QInputDialog, QFileDialog, QProgressBar, QLabel, QHBoxLayout, QGridLayout
from PyQt6.QtGui import QPixmap, QAction, QCursor, QFontMetrics
from PyQt6.QtCore import Qt, QTimer
from NetDisk import Ui_NetDiskWindow
import time

TIMESLICE = 1000


class MyProgress(QtWidgets.QWidget):
    def __init__(self):
        super(MyProgress, self).__init__()
        self.isPause = None
        self.timer = None
        self.progress = None
        self.label_2 = None
        self.label = None
        self.gridlayout = None
        self.setContentsMargins(0, 0, 0, 0)
        self.initUI()
        self.rest_time = 0
        self.speed = 160000
        self.fsize = 0
        self.last_time = time.time()
        self.last_value = None

    def initUI(self):
        self.gridlayout = QGridLayout(self)
        # self.hblayout = QHBoxLayout(self)
        self.label = QLabel(self)
        self.label.setFixedWidth(100)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2 = QLabel(self)
        self.label_2.setFixedWidth(100)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar(self)
        self.progress.setFixedWidth(200)
        self.gridlayout.addWidget(self.label, 0, 0, 4, 0)
        self.gridlayout.addWidget(self.label_2, 0, 1, 4, 0)
        self.gridlayout.addWidget(self.progress, 0, 2, 4, 2)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerOn)

        # self.mouseDoubleClickEvent.connect(self.doubleclick)
        # self.hblayout.addWidget(self.label)
        # self.hblayout.addWidget(self.progress)
        # self.setLayout(self.hblayout)

    def setFileNameText(self, text):
        fontWidth = QFontMetrics(self.font())
        elideNote = fontWidth.elidedText(text, Qt.TextElideMode.ElideRight, self.label.width())
        self.label.setText(elideNote)
        self.label.setToolTip(text)

    def setFSize(self, fsize):
        self.fsize = fsize
        self.progress.setMaximum(fsize)

    def setProgressValue(self, value):
        if value > self.fsize:
            value = self.fsize
        self.progress.setValue(value)
        if self.last_value is not None:
            try:
                self.speed = (value - self.last_value) / (time.time() - self.last_time)
            except Exception as e:
                self.speed = 160000
            if self.speed == 0:
                self.speed = 160000
        self.rest_time = (self.fsize - value) / self.speed
        self.last_value = value
        self.last_time = time.time()

    def start(self):
        self.timer.start(TIMESLICE)

    def timerOn(self):
        self.rest_time -= 1
        if self.rest_time < 5:
            self.rest_time = 5
        text = time.strftime("%H:%M:%S", time.gmtime(self.rest_time))
        fontWidth = QFontMetrics(self.label_2.font())
        elideNote = fontWidth.elidedText(text, Qt.TextElideMode.ElideRight, self.label_2.width())
        self.label_2.setText(elideNote)
        self.label_2.setToolTip(text)
        newValue = self.last_value + self.speed * (time.time() - self.last_time)
        self.progress.setValue(newValue)

    def finish(self):
        self.setProgressValue(self.fsize)
        self.timer.stop()
        self.label_2.setText("已完成")

    def pause(self):
        self.isPause = True
        self.timer.stop()
        self.label_2.setText("暂停")

    def restart(self):
        self.isPause = True
        self.speed = 160000
        self.last_time = time.time()
        self.timer.start(TIMESLICE)

