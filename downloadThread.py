import os.path
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, QWaitCondition
import hashlib
from client import client
import chardet
import time
import config
import re
import os
import math
from hashlib import md5
import shutil

MAX_FRAGMENT_SIZE = 4 * 1024 * 1024

FRAG_SIZE = 4 * 1024 * 1024


class DownloadFileThread(QThread):
    trigger = QtCore.pyqtSignal(int, str)

    # console = QtCore.pyqtSignal(str)

    def __init__(self):
        super(DownloadFileThread, self).__init__()
        self.tmp_path = None
        self.fsize = None
        self.fdid = None
        self.save_path = None
        self.download_index = None
        self.user_config = None
        self.current_user = None
        self.client = None
        self.filename = None
        self.isPause = False

    def setOption(self, download_index: int, save_path: str, filename: str, fdid: int, fsize: int):
        print("set option")
        self.download_index = download_index
        self.save_path = save_path
        self.filename = filename
        self.fdid = fdid
        self.fsize = fsize
        self.trigger.connect(self.triggerRecv)
        self.client = client()
        self.current_user = config.get_current_user()
        self.user_config = config.get_user_config(self.current_user)
        self.client.headers['Cookie'] = self.user_config['Cookie']
        self.tmp_path = self.user_config['tmp_path']

    def __del__(self):
        self.wait()

    def run(self) -> None:
        try:
            self.trigger.emit(self.download_index, "start")
            # self.uploadFile(self.filePath, self.pid)
            self.downloadFile(self.fdid, self.save_path, self.filename)
            self.trigger.emit(self.download_index, "success")

        except Exception as e:
            self.trigger.emit(self.download_index, repr(e))
        # pass

    def downloadFile(self, fdid, save_path, filename):
        frag_dir_path = os.path.join(self.tmp_path, str(fdid))
        if not os.path.exists(frag_dir_path):
            os.makedirs(frag_dir_path)
        max_index = math.ceil(self.fsize / MAX_FRAGMENT_SIZE)
        index = 0
        while index < max_index:
            if self.isPause:
                time.sleep(0.1)
                continue
            self.download_frag(fdid, frag_dir_path, index)
            self.trigger.emit(self.download_index, str(index))
            index += 1
            pass
        self.combine(filename, save_path, frag_dir_path)

    def triggerRecv(self, download_index, message):
        if download_index == -1:
            self.isPause = not self.isPause
            print("download isPause:", self.isPause, download_index, message)

    def download_frag(self, fdid, frag_dir_path, index):
        frag_bits = self.client.download_fragment(fdid, index)
        if isinstance(frag_bits, dict):
            print("下载错误", frag_bits)
        else:
            print("下载碎片成功")
            with open(os.path.join(frag_dir_path, str(index)), "wb") as fp:
                fp.write(frag_bits)

    def combine(self, filename: str, file_save_path: str, file_tmp_path: str):
        # save_list = os.listdir(file_save_path)
        # if filename in save_list:
        #     # 给出一个提示,确认是否覆盖文件
        #     # 覆盖的话对文件名不进行任何操作
        #     # 若不覆盖则替换文件名
        #     pos = filename.rfind(".")
        #     if pos == -1:
        #         filename += "_1"
        #     else:
        #         filename = filename[:pos] + "_1" + filename[pos:]
        with open(os.path.join(file_save_path, filename), "wb") as fp:
            frag_list = os.listdir(file_tmp_path)
            frag_list.sort(key=lambda x: int(x))
            for i in frag_list:
                frag_fp = open(os.path.join(file_tmp_path, str(i)), "rb")
                fp.write(frag_fp.read())
                frag_fp.close()
            shutil.rmtree(file_tmp_path)


#
# class DownloadDirThread(QThread):
#     trigger = QtCore.pyqtSignal(int, str)
#
#     # console = QtCore.pyqtSignal(str)
#
#     def __init__(self):
#         super(DownloadDirThread, self).__init__()
#         self.tmp_path = None
#         self.fsize = None
#         self.fdid = None
#         self.save_path = None
#         self.download_index = None
#         self.user_config = None
#         self.current_user = None
#         self.client = None
#         self.filename = None
#         self.isPause = False
#
#     def setOption(self, download_index: int, save_path: str, filename:str, fdid: int, fsize: int):
#         print("set option")
#         self.download_index = download_index
#         self.save_path = save_path
#         self.filename = filename
#         self.fdid = fdid
#         self.fsize = fsize
#         self.trigger.connect(self.triggerRecv)
#         self.client = client()
#         self.current_user = config.get_current_user()
#         self.user_config = config.get_user_config(self.current_user)
#         self.client.headers['Cookie'] = self.user_config['Cookie']
#         self.tmp_path = self.user_config['tmp_path']
#
#     def __del__(self):
#         self.wait()
#
#     def run(self) -> None:
#         try:
#             self.trigger.emit(self.download_index, "start")
#             # self.uploadFile(self.filePath, self.pid)
#             self.downloadFile(self.fdid, self.save_path, self.filename)
#             self.trigger.emit(self.download_index, "success")
#
#         except Exception as e:
#             self.trigger.emit(self.download_index, repr(e))
#         # pass
#
#     def downloadFile(self, fdid, save_path, filename):
#         frag_dir_path = os.path.join(self.tmp_path, str(fdid))
#         if not os.path.exists(frag_dir_path):
#             os.makedirs(frag_dir_path)
#         max_index = math.ceil(self.fsize / MAX_FRAGMENT_SIZE)
#         index = 0
#         while index < max_index:
#             if self.isPause:
#                 time.sleep(0.1)
#                 continue
#             self.download_frag(fdid, frag_dir_path, index)
#             self.trigger.emit(self.download_index, str(index))
#             index += 1
#             pass
#         self.combine(filename, save_path, frag_dir_path)
#
#     def triggerRecv(self, download_index, message):
#         if download_index == -1:
#             self.isPause = not self.isPause
#             print("download isPause:", self.isPause, download_index, message)
#
#     def download_frag(self, fdid, frag_dir_path, index):
#         frag_bits = self.client.download_fragment(fdid, index)
#         if isinstance(frag_bits, dict):
#             print("下载错误", frag_bits)
#         else:
#             print("下载碎片成功")
#             with open(os.path.join(frag_dir_path, str(index)), "wb") as fp:
#                 fp.write(frag_bits)
#
#     def combine(self, filename: str, file_save_path: str, file_tmp_path: str):
#         # save_list = os.listdir(file_save_path)
#         # if filename in save_list:
#         #     # 给出一个提示,确认是否覆盖文件
#         #     # 覆盖的话对文件名不进行任何操作
#         #     # 若不覆盖则替换文件名
#         #     pos = filename.rfind(".")
#         #     if pos == -1:
#         #         filename += "_1"
#         #     else:
#         #         filename = filename[:pos] + "_1" + filename[pos:]
#         with open(os.path.join(file_save_path, filename), "wb") as fp:
#             frag_list = os.listdir(file_tmp_path)
#             frag_list.sort(key=lambda x: int(x))
#             for i in frag_list:
#                 frag_fp = open(os.path.join(file_tmp_path, str(i)), "rb")
#                 fp.write(frag_fp.read())
#                 frag_fp.close()
#             shutil.rmtree(file_tmp_path)


class DownloadDirThread(QThread):
    trigger = QtCore.pyqtSignal(int, str)

    # console = QtCore.pyqtSignal(str)

    def __init__(self):
        super(DownloadDirThread, self).__init__()
        self.tmp_path = None
        self.totalSize = None
        self.save_path = None
        self.did = None
        self.user_config = None
        self.current_user = None
        self.file_download_list = None
        self.client = None
        self.download_index = None

        self.isPause = False
        self.haveDownload = 0

    def setOption(self, download_index: int, did: int, save_path: str):
        print("set option")
        self.download_index = download_index
        self.did = did
        self.save_path = save_path
        self.trigger.connect(self.triggerRecv)
        self.client = client()
        self.current_user = config.get_current_user()
        self.user_config = config.get_user_config(self.current_user)
        self.client.headers['Cookie'] = self.user_config['Cookie']
        self.tmp_path = self.user_config['tmp_path']
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
            self.create_all_dir()
            # print("create dir")
            self.trigger.emit(self.download_index, "start")
            # print("emit start",self.file_download_list)
            for file_download in self.file_download_list:
                # print("download file", file_download['filename'])
                self.downloadFile(file_download)
                self.haveDownload += file_download['fsize']
            # print("download file end", file_download['filename'])
            # self.trigger.emit(self.download_index, "file_downloaded")
            self.trigger.emit(self.download_index, "start")
            self.downloadFile(self.filePath, self.pid)
            self.trigger.emit(self.download_index, "success")

        except Exception as e:
            self.trigger.emit(self.download_index, repr(e))
        # pass

    # def downloadDir(self, dirpath, pid):
    #
    #     pass
    def create_all_dir(self):

        ans = self.client.get_tree(self.did)
        print(ans)

        tree_list = ans['data']
        self.file_download_list = []

        self.totalSize = 0
        self.traverseTreeList(tree_list, self.save_path)
        print(self.file_download_list)
        self.user_config['download_list'][
            self.download_index]['file_download_list'] = self.file_download_list
        self.user_config['download_list'][self.download_index]['totalSize'] = self.totalSize
        config.set_user_config(self.current_user, self.user_config)

    def traverseTreeList(self, tree_list, path):
        for tree in tree_list:
            if tree['type'] == 0:
                new_path = os.path.join(path, tree['name'])
                if os.path.exists(new_path):
                    ans = self.client.get_md5code(tree['id'])
                    file_md5 = ans['data']['MD5']
                    new_name = tree['name']
                    hasMD5 = False
                    while True:
                        test_md5 = hashlib.md5(open(os.path.join(path, new_name), "rb").read())
                        if test_md5 == file_md5:
                            hasMD5 = True
                            break
                        new_name_vec = new_name.split('.')
                        if len(new_name_vec) > 1:
                            new_name_vec[-2] += "-副本"
                            new_name = '.'.join(new_name_vec)
                        else:
                            new_name += "副本"
                        new_path = os.path.join(path, new_name)
                        if not os.path.exists(new_path):
                            break
                    if hasMD5:
                        continue

                self.totalSize += tree['size']
                self.file_download_list.append({
                    "fdid": tree['id'],
                    "save_path": new_path,
                    "index": 0,
                    "fsize": tree['size'],
                    "filename": tree['name']
                })
            else:
                next_path = os.path.join(path, tree['label'])
                if not os.path.exists(next_path):
                    os.makedirs(next_path)
                self.traverseTreeList(tree['children'], next_path)

    def downloadFile(self, file_download):
        save_path = file_download['save_path']
        fdid = file_download['fdid']
        fsize = file_download['fsize']
        filename = file_download['filename']
        frag_dir_path = os.path.join(self.tmp_path, str(fdid))
        if not os.path.exists(frag_dir_path):
            os.makedirs(frag_dir_path)
        max_index = math.ceil(fsize / MAX_FRAGMENT_SIZE)
        index = 0
        while index < max_index:
            if self.isPause:
                time.sleep(0.1)
                continue
            self.download_frag(fdid, frag_dir_path, index)
            self.trigger.emit(self.download_index,
                              str(self.haveDownload + min((index + 1) * MAX_FRAGMENT_SIZE, fsize)))
            index += 1
            pass
        self.combine(save_path, frag_dir_path)

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

    def download_frag(self, fdid, frag_dir_path, index):
        frag_bits = self.client.download_fragment(fdid, index)
        if isinstance(frag_bits, dict):
            print("下载错误", frag_bits)
        else:
            print("下载碎片成功")
            with open(os.path.join(frag_dir_path, str(index)), "wb") as fp:
                fp.write(frag_bits)

    def combine(self, file_save_path: str, file_tmp_path: str):
        with open(file_save_path, "wb") as fp:
            frag_list = os.listdir(file_tmp_path)
            frag_list.sort(key=lambda x: int(x))
            for i in frag_list:
                frag_fp = open(os.path.join(file_tmp_path, str(i)), "rb")
                fp.write(frag_fp.read())
                frag_fp.close()
            shutil.rmtree(file_tmp_path)
