import os
import json


# default_config = {
#     'tmp_path': 'D://TJ-NETDISK-TMP',
# }


def _init():
    global _config_dict
    if not os.path.exists('config.json'):
        _config_dict = {'current_user': '', 'user_config': {}}
        json.dump(_config_dict, open('config.json', 'w'))
    else:
        _config_dict = json.load(open('config.json', 'r'))


# # 设置字典内容
# def set_value(name, value):
#     _config_dict[name] = value
#     json.dump(_config_dict, open('config.json','w'))
#
#
# # 读取字典内容
# def get_value(name, defValue=None):
#     try:
#         return _config_dict[name]
#     except KeyError:
#         return defValue

# 设置字典内容
def set_current_user(user_name):
    _config_dict['current_user'] = user_name
    json.dump(_config_dict, open('config.json', 'w'))


def set_user_config(user, value):
    _config_dict['user_config'][user] = value
    json.dump(_config_dict, open('config.json', 'w'))


# 读取字典内容
def get_current_user():
    return _config_dict['current_user']


def get_user_config(user, defValue=None):
    try:
        return _config_dict['user_config'][user]
    except KeyError:
        return defValue


