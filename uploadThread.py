import os.path
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, QWaitCondition
import hashlib
from client import client
import chardet
import time
import config
import re
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
        super(UploadDirThread, self).__init__()
        self.user_config = None
        self.current_user = None
        self.file_upload_list = None
        self.client = None
        self.dirpath = None
        self.upload_index = None
        self.pid = None
        self.filePath = None
        self.isPause = False
        self.haveUpload = 0

    def setOption(self, upload_index: int, dirpath: str, pid: int):
        print("set option")
        self.upload_index = upload_index
        self.dirpath = dirpath
        self.pid = pid
        self.trigger.connect(self.triggerRecv)
        self.client = client()
        self.current_user = config.get_current_user()
        self.user_config = config.get_user_config(self.current_user)
        self.client.headers['Cookie'] = self.user_config['Cookie']

    def __del__(self):
        self.wait()

    def run(self) -> None:
        try:
            self.create_all_dir()
            print("create dir")
            self.trigger.emit(self.upload_index, "start")
            print("emit start",self.file_upload_list)
            for file_upload in self.file_upload_list:
                # print("upload file", file_upload['filename'])
                self.uploadFile(file_upload)
                self.haveUpload += file_upload['fsize']
                # print("upload file end", file_upload['filename'])
                # self.trigger.emit(self.upload_index, "file_uploaded")
            self.trigger.emit(self.upload_index, "success")

        except Exception as e:
            self.trigger.emit(self.upload_index, repr(e))
        # pass

    # def uploadDir(self, dirpath, pid):
    # 
    #     pass
    def create_all_dir(self):

        dirname = self.dirpath.split('/')[-1]
        ans = self.client.create_dir(self.pid, dirname)
        print(ans)
        dirMap = {self.dirpath: ans['data']['did']}
        fileMap = {}
        totalSize = 0
        for root, dirs, files in os.walk(self.dirpath):
            print(root, dirs, files)
            for subdir in dirs:
                ans = self.client.create_dir(dirMap[root], subdir)
                print(ans)
                dirMap[os.path.join(root, subdir)] = ans['data']['did']

            for file in files:
                fileMap[os.path.join(root, file)] = dirMap[root]
                totalSize += os.path.getsize(os.path.join(root, file))
        print(fileMap)
        print(dirMap)
        print(totalSize)
        self.file_upload_list = []
        print("file map", fileMap)
        for (key, value) in fileMap.items():
            self.file_upload_list.append({"filepath": key, "pid": value, "fsize": os.path.getsize(key), "index": 0})

        self.user_config['upload_list'][self.upload_index]['file_upload_list'] = self.file_upload_list
        self.user_config['upload_list'][self.upload_index]['totalSize'] = totalSize
        config.set_user_config(self.current_user, self.user_config)




    def uploadFile(self, file_upload):
        filepath = file_upload['filepath']
        pid = file_upload['pid']
        fsize = os.path.getsize(filepath)
        filename = filepath.split('/')[-1].split("\\")[-1]
        print(filename,filepath)
        with open(filepath, 'rb') as file:
            content = file.read()
        full_md5 = hashlib.md5(content).hexdigest()
        print(filename, full_md5)
        ans = self.client.get_file_exist(full_md5)
        print(ans)
        if ans['data']['is_exist']:
            ans = self.client.upload_file(filename, pid, full_md5)
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

                ans = self.client.get_upload_allocation(full_md5, fsize)
                print(ans)
                next_index = ans['data']['next_index']
                print("next_index", next_index)
                if next_index == -1:
                    break
                fragment = content[next_index * FRAG_SIZE:min((next_index + 1) * FRAG_SIZE, fsize)]
                fragment_md5 = hashlib.md5(fragment).hexdigest()
                print("fragment:", next_index, "md5:", fragment_md5)
                ans = self.client.get_file_fragment_exist(fragment_md5)
                print(ans)
                frag_exist = ans['data']['is_exist']
                if frag_exist:
                    ans = self.client.upload_fragment(next_index, full_md5, fragment_md5)
                else:
                    ans = self.client.upload_fragment(next_index, full_md5, fragment_md5, fragment)
                print(ans)
                print("current size",self.haveUpload+min((next_index+1)*FRAG_SIZE,file_upload['fsize']))
                self.trigger.emit(self.upload_index, str(self.haveUpload+min((next_index+1)*FRAG_SIZE,file_upload['fsize'])))
            ans = self.client.upload_file(filename, pid, full_md5)
            print(ans)
            if ans['message'] == "success":
                return
            else:
                print("upload error")

    def triggerRecv(self, upload_index, message):
        if upload_index == -1:
            self.isPause = not self.isPause
            print("upload isPause:", self.isPause, upload_index, message)
