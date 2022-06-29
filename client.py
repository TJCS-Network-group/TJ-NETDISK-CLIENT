import requests
from typing import Union
# import httpx
import json
import hashlib


class client(object):
    def __init__(self):
        self.host = "http://121.37.159.103:7777"
        self.headers = dict()

    def logout(self):
        req = requests.get(url=self.host + "/api/logout", headers=self.headers)
        ans = json.loads(req.text)
        self.headers.pop("Cookie")
        return ans

    def get_dir_tree(self):
        req = requests.get(self.host + "/api/share/get_dir_tree", headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_myinfo(self):
        req = requests.get(self.host + "/api/myinfo", headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_identity(self):
        req = requests.get(self.host + "/api/get_identity", headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_root_id(self):
        req = requests.get(self.host + "/api/get_root_id", headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_dir(self, dir_id: int):
        req = requests.get(self.host + "/api/filesystem/get_dir", params={"dir_id": dir_id}
                           , headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_upload_allocation(self, md5code: str, size: Union[int, None]):
        params = {"md5": md5code}
        if size is not None:
            params["size"] = size
        req = requests.get(self.host + "/api/upload_allocation", params=params, headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_file_exist(self, md5code: str):
        req = requests.get(self.host + "/api/file_exist", params={"md5": md5code}, headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_file_fragment_exist(self, md5code: str):
        req = requests.get(self.host + "/api/file_fragment_exist", params={"md5": md5code}, headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def get_tree(self,did:int):
        req = requests.get(self.host+"/api/filesystem/get_tree",params={"did":did},headers=self.headers)
        ans = json.loads(req.text)
        return ans

    def download_fragment(self, fdid: int, index: int):
        req = requests.get(self.host + "/api/download_fragment", params={"fdid": fdid, "index": index},
                           headers=self.headers)
        if req.headers["Content-Type"] == "application/json;charset=GBK":
            ans = json.loads(req.text)
        else:
            ans = req.content
        return ans

    def register(self, user_name: str, password: str):
        self.headers['content-type'] = 'application/json'
        req = requests.post(url=self.host + "/api/register", headers=self.headers,
                            data=json.dumps({"user_name": user_name, "password": password}))
        ans = json.loads(req.text)
        return ans

    def login(self, user_name: str, password: str):
        self.headers['content-type'] = 'application/json'
        req = requests.post(url=self.host + "/api/login", headers=self.headers,
                            data=json.dumps({"user_name": user_name, "password": password}))
        self.headers.pop('content-type')
        self.headers["Cookie"] = (req.headers["Set-Cookie"])
        ans = json.loads(req.text)
        return ans

    def create_dir(self, pid: int, dname: str):
        self.headers['content-type'] = 'application/json'
        req = requests.post(self.host + "/api/filesystem/create_dir", headers=self.headers
                            , data=json.dumps({"pid": pid, "dname": dname}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def remove_dir(self, dir_id: int):
        self.headers['content-type'] = 'application/json'
        req = requests.delete(self.host + "/api/remove_dir", headers=self.headers
                              , data=json.dumps({"dir_id": dir_id}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def remove_file(self, fdid: int):
        self.headers['content-type'] = 'application/json'
        req = requests.delete(self.host + "/api/remove_file", headers=self.headers
                              , data=json.dumps({"fdid": fdid}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def rename_dir(self, did: int, dname: str):
        self.headers['content-type'] = 'application/json'
        req = requests.put(self.host + "/api/filesystem/rename_dir", headers=self.headers,
                           data=json.dumps({"did": did, "dname": dname}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def rename_file(self, fid: int, fname: str):
        self.headers['content-type'] = 'application/json'
        req = requests.put(self.host + "/api/filesystem/rename_file", headers=self.headers,
                           data=json.dumps({"fid": fid, "fname": fname}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def move_file(self, fdid: int, pid: int):
        self.headers['content-type'] = 'application/json'
        req = requests.post(self.host + "/api/share/move_file", headers=self.headers,
                            data=json.dumps({"fdid": fdid, "pid": pid}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def copy_file(self, fdid: int, pid: int):
        self.headers['content-type'] = 'application/json'
        req = requests.post(self.host + "/api/share/copy_file", headers=self.headers,
                            data=json.dumps({"fdid": fdid, "pid": pid}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def move_dir(self, did: int, pid: int):
        self.headers['content-type'] = 'application/json'
        req = requests.post(self.host + "/api/share/move_dir", headers=self.headers,
                            data=json.dumps({"did": did, "pid": pid}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def copy_dir(self, did: int, pid: int):
        self.headers['content-type'] = 'application/json'
        req = requests.post(self.host + "/api/share/copy_dir", headers=self.headers,
                            data=json.dumps({"did": did, "pid": pid}))
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def upload_file(self, filename: str, parent_dir_id: int, md5code: str):
        self.headers['content-type'] = 'application/json'
        body = json.dumps({"filename": filename, "parent_dir_id": parent_dir_id, "md5": md5code}, ensure_ascii=False).encode('utf-8')
        req = requests.post(self.host + "/api/upload_file", headers=self.headers,
                            data=body)
        self.headers.pop('content-type')
        ans = json.loads(req.text)
        return ans

    def upload_fragment(self, index: int, file_md5code: str, fragment_md5code: str, fragment=None):
        if fragment is None:
            req = requests.post(self.host + "/api/upload_fragment", headers=self.headers,
                                data={"index": index, "file_md5": file_md5code, "fragment_md5": fragment_md5code})
        else:
            req = requests.post(self.host + "/api/upload_fragment", headers=self.headers,
                                data={"index": index, "file_md5": file_md5code, "fragment_md5": fragment_md5code},
                                files=[("file_fragment", ("file_fragment", fragment))])
        ans = json.loads(req.text)
        return ans
