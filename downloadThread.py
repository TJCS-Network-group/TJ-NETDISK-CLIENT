import os.path
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, QWaitCondition
import hashlib
from client import client
import chardet
import time
import config

FRAG_SIZE = 4 * 1024 * 1024


class DownloadFileThread(QThread):
    trigger = QtCore.pyqtSignal(int, str)

    # console = QtCore.pyqtSignal(str)

    def __init__(self):
        super(DownloadFileThread, self).__init__()
        self.download_index = None
        self.filename = None
        self.filesize = None
        self.fdid = None
        self.filePath = None
        self.isPause = False

    def setOption(self, download_index: int, filePath: str, pid: int):
        print("set option")
        self.download_index = download_index
        self.filePath = filePath
        self.pid = pid
        self.trigger.connect(self.triggerRecv)

    def __del__(self):
        self.wait()

    def run(self) -> None:
        try:
            self.trigger.emit(self.download_index, "start")
            self.downloadFile(self.filePath, self.pid)
            self.trigger.emit(self.download_index, "success")

        except Exception as e:
            self.trigger.emit(self.download_index, repr(e))
        # pass

    def downloadFile(self, filePath, fdid):
        c = client()
        c.headers['Cookie'] = config.get_user_config(config.get_current_user())['Cookie']
        #  检查filePath处是否存在文件


        # 不存在则下载

        #？获取文件信息

        index = self.index
        while True:
            if self.isPause:
                time.sleep(1)
                continue



    def triggerRecv(self, download_index, message):
        if download_index == -1:
            self.isPause = not self.isPause
            print("download isPause:", self.isPause, download_index, message)


