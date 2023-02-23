import re
import attr
from typing import Callable
import json
import traceback
import requests

UPLOAD_URL = 'http://localhost:5700'

@attr.s(auto_attribs=True)
class _SHandler:
    call_back:Callable[[dict],bool]
    # 返回JSON数据
    # 返回bool,指示是否继续传播
    call_type:str
    # message
    # meta
    # ...
    call_match:dict = {}

_handlers:list[_SHandler] = []

def on_message(**match):
    def dect(func:Callable):
        _handlers.append(_SHandler(func,'message',match))
        return func
    return dect

def mark_as_read(data:dict):
    res = requests.post(f'{UPLOAD_URL}/mark_msg_as_read',params={
        'message_id':data['message_id']
    })
    if res.status_code != 200:
        raise Exception("状态错误")

def send_user_back(data:dict,message:str):
    res = requests.post(f"{UPLOAD_URL}/send_private_msg",params={
        'user_id':data['user_id'],
        'message':message
    })
    if res.status_code != 200:
        raise Exception("状态错误")

def _handle_(data:dict):
    for i in _handlers:
        if i.call_type == data['post_type']:
            if all([
                bool(mem[1].match(data[mem[0]])) 
                if isinstance(mem[1],re.Pattern) else data[mem[0]] == mem[1] 
                for mem in i.call_match.items()]):
                try:
                    if i.call_back(data) == False:
                        break
                except Exception as e:
                    traceback.print_exception(e)
