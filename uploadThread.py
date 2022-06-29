import os.path
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, QWaitCondition
import hashlib
from client import client
import chardet
import time
import config

FRAG_SIZE = 4 * 1024 * 1024


class UploadFileThread(QThread):
    trigger = QtCore.pyqtSignal(int, str)

    # console = QtCore.pyqtSignal(str)

    def __init__(self):
        super(UploadFileThread, self).__init__()
        self.upload_index = None
        self.filename = None
        self.pid = None
        self.filePath = None
        self.isPause = False

    def setOption(self, upload_index: int, filePath: str, pid: int):
        print("set option")
        self.upload_index = upload_index
        self.filePath = filePath
        self.pid = pid
        self.trigger.connect(self.triggerRecv)

    def __del__(self):
        self.wait()

    def run(self) -> None:
        try:
            self.trigger.emit(self.upload_index, "start")
            self.uploadFile(self.filePath, self.pid)
            self.trigger.emit(self.upload_index, "success")

        except Exception as e:
            self.trigger.emit(self.upload_index, repr(e))
        # pass

    def uploadFile(self, filePath, pid):
        c = client()
        c.headers['Cookie'] = config.get_user_config(config.get_current_user())['Cookie']
        fsize = os.path.getsize(filePath)
        filename = filePath.split('/')[-1]
        # print(type(filename), chardet.detect(filename))
        with open(filePath, 'rb') as file:
            content = file.read()
        full_md5 = hashlib.md5(content).hexdigest()
        print(filename, full_md5)
        ans = c.get_file_exist(full_md5)
        print(ans)
        if ans['data']['is_exist']:
            ans = c.upload_file(filename, pid, full_md5)
            print(ans)
            if ans['message'] == "success":
                return
            else:
                print("upload error")
        else:

            while True:
                if self.isPause:
                    time.sleep(1)
                    continue

                ans = c.get_upload_allocation(full_md5, fsize)
                print(ans)
                next_index = ans['data']['next_index']
                print("next_index", next_index)
                if next_index == -1:
                    break
                fragment = content[next_index * FRAG_SIZE:min((next_index + 1) * FRAG_SIZE, fsize)]
                fragment_md5 = hashlib.md5(fragment).hexdigest()
                print("fragment:", next_index, "md5:", fragment_md5)
                ans = c.get_file_fragment_exist(fragment_md5)
                print(ans)
                frag_exist = ans['data']['is_exist']
                if frag_exist:
                    ans = c.upload_fragment(next_index, full_md5, fragment_md5)
                else:
                    ans = c.upload_fragment(next_index, full_md5, fragment_md5, fragment)
                print(ans)
                self.trigger.emit(self.upload_index, str(next_index))
            ans = c.upload_file(filename, pid, full_md5)
            print(ans)
            if ans['message'] == "success":
                return
            else:
                print("upload error")

    def triggerRecv(self, upload_index, message):
        if upload_index == -1:
            self.isPause = not self.isPause
            print("upload isPause:", self.isPause, upload_index, message)



class UploadDirThread(QThread):
    trigger = QtCore.pyqtSignal(int, str)

    # console = QtCore.pyqtSignal(str)

    def __init__(self):
        super(UploadFileThread, self).__init__()
        self.upload_index = None
        self.filename = None
        self.pid = None
        self.filePath = None
        self.isPause = False

    def setOption(self, upload_index: int, filePath: str, pid: int):
        print("set option")
        self.upload_index = upload_index
        self.filePath = filePath
        self.pid = pid
        self.trigger.connect(self.triggerRecv)

    def __del__(self):
        self.wait()

    def run(self) -> None:
        try:
            self.trigger.emit(self.upload_index, "start")
            self.uploadFile(self.filePath, self.pid)
            self.trigger.emit(self.upload_index, "success")

        except Exception as e:
            self.trigger.emit(self.upload_index, repr(e))
        # pass

    def uploadDir(self, dirpath, pid):

        pass


    def uploadFile(self, filePath, pid):
        c = client()
        c.headers['Cookie'] = config.get_user_config(config.get_current_user())['Cookie']
        fsize = os.path.getsize(filePath)
        filename = filePath.split('/')[-1]
        # print(type(filename), chardet.detect(filename))
        with open(filePath, 'rb') as file:
            content = file.read()
        full_md5 = hashlib.md5(content).hexdigest()
        print(filename, full_md5)
        ans = c.get_file_exist(full_md5)
        print(ans)
        if ans['data']['is_exist']:
            ans = c.upload_file(filename, pid, full_md5)
            print(ans)
            if ans['message'] == "success":
                return
            else:
                print("upload error")
        else:

            while True:
                if self.isPause:
                    time.sleep(1)
                    continue

                ans = c.get_upload_allocation(full_md5, fsize)
                print(ans)
                next_index = ans['data']['next_index']
                print("next_index", next_index)
                if next_index == -1:
                    break
                fragment = content[next_index * FRAG_SIZE:min((next_index + 1) * FRAG_SIZE, fsize)]
                fragment_md5 = hashlib.md5(fragment).hexdigest()
                print("fragment:", next_index, "md5:", fragment_md5)
                ans = c.get_file_fragment_exist(fragment_md5)
                print(ans)
                frag_exist = ans['data']['is_exist']
                if frag_exist:
                    ans = c.upload_fragment(next_index, full_md5, fragment_md5)
                else:
                    ans = c.upload_fragment(next_index, full_md5, fragment_md5, fragment)
                print(ans)
                self.trigger.emit(self.upload_index, str(next_index))
            ans = c.upload_file(filename, pid, full_md5)
            print(ans)
            if ans['message'] == "success":
                return
            else:
                print("upload error")

    def triggerRecv(self, upload_index, message):
        if upload_index == -1:
            self.isPause = not self.isPause
            print("upload isPause:", self.isPause, upload_index, message)
