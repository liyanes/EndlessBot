from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import re
import attr
from typing import Callable, Literal, overload,Iterable,Any
import json
import traceback
import requests
import os

RECEIVE_PORT = 5701
UPLOAD_URL = 'http://localhost:5700'

class LimitList(list):

    @overload
    def __init__(self, limit_len: int = 200) -> None:
        ...

    @overload
    def __init__(self, __iterable: Iterable[Any], limit_len: int = 200) -> None:
        ...

    def __init__(self, *args, **kwargs):
        if 'limit_len' in kwargs:
            self.limit_len = kwargs['limit_len']
            del kwargs['limit_len']
        else:
            if len(args) >= 1:
                if isinstance(args[0], int):
                    self.limit_len = args[0]
                    args = args[1:]
                else:
                    self.limit_len = 200
            else:
                self.limit_len = 200
        super().__init__(*args, **kwargs)

    def append(self, __object) -> None:
        if len(self) >= self.limit_len:self.pop(0)
        return super().append(__object)

messageHis = LimitList()

class Message(dict):
    @property
    def type(self) -> Literal['message','request','notice','meta_event']:
        return self['post_type']
    
    @property
    def message_id(self) -> int:
        return self['message_id']
    
    @property
    def message(self) -> str:
        return self['message']
    
    @property
    def user_id(self) -> int:
        return self['user_id']
    
    def send(self,message:str) -> int:
        if self.type == 'message':
            if self['message_type'] == 'private':
                self._send_private(message)
                return self['user_id']
            elif self['message_type'] == 'group':
                self._send_group(message)
                return self['group_id']
        raise Exception("不支持的消息类型")
    
    def _send_private(self,message:str):
        res = requests.post(f"{UPLOAD_URL}/send_private_msg",params={
            'user_id':self['user_id'],
            'message':message
        })
        if res.status_code != 200:
            raise Exception("状态错误")
        
    def _send_group(self,message:str):
        res = requests.post(f"{UPLOAD_URL}/send_group_msg",params={
            'group_id':self['group_id'],
            'message':message
        })
        if res.status_code != 200:
            raise Exception("状态错误")

    def mark_read(self):
        res = requests.post(f'{UPLOAD_URL}/mark_msg_as_read',params={
            'message_id':self['message_id']
        })
        if res.status_code != 200:
            raise Exception("状态错误")
    
    def accept(self) -> int:
        if self.type == 'request':
            if self['request_type'] == 'friend':
                self._enable_friend()
                return self['user_id']
            elif self['request_type'] == 'group':
                self._enable_group()
                return self['group_id']
        raise Exception("不支持的消息类型")

    def _enable_friend(self):
        res = requests.post(f'{UPLOAD_URL}/set_friend_add_request',params={
            'flag':self['flag'],
            'approve':True
        })
        if res.status_code != 200:
            raise Exception("状态错误")
        
    def _enable_group(self):
        res = requests.post(f'{UPLOAD_URL}/set_group_add_request',params={
            'flag':self['flag'],
            'approve':True,
            'type':'invite'
        })
        if res.status_code != 200:
            raise Exception("状态错误")
        
    def delete_friend(self):
        res = requests.post(f'{UPLOAD_URL}/delete_friend',params={
            'user_id':self['user_id']
        })
        if res.status_code != 200:
            raise Exception("状态错误")

def send(user_id:int,message:str):
    res = requests.post(f"{UPLOAD_URL}/send_private_msg",params={
        'user_id':user_id,
        'message':message
    })
    if res.status_code != 200:
        raise Exception("状态错误")

def enable_friend(flag:str):
    res = requests.post(f'{UPLOAD_URL}/set_friend_add_request',params={
        'flag':flag,
        'approve':True
    })
    if res.status_code != 200:
        raise Exception("状态错误")
    
def enable_group(flag:str):
    res = requests.post(f'{UPLOAD_URL}/set_group_add_request',params={
        'flag':flag,
        'approve':True,
        'type':'invite'
    })
    if res.status_code != 200:
        raise Exception("状态错误")

def delete_friend(user_id:int):
    res = requests.post(f'{UPLOAD_URL}/delete_friend',params={
        'user_id':user_id
    })
    if res.status_code != 200:
        raise Exception("状态错误")
    
def get_friend_list():
    res = requests.get(f'{UPLOAD_URL}/get_friend_list')
    if res.status_code != 200:
        raise Exception("状态错误")
    return res.json()['data']

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args):
        return

    def do_POST(self):
        req_body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        req_json = json.loads(req_body)

        if req_json['post_type'] == 'message':
            if req_json['message_id'] in messageHis:
                return
            else:
                messageHis.append(req_json['message_id'])
        
        self.send_response(200)
        self.end_headers()

        _handle_(Message(req_json))

def start_handler():
    th = ThreadingHTTPServer(('localhost',RECEIVE_PORT),Handler)
    try:
        th.serve_forever()
    except KeyboardInterrupt:
        ...

@attr.s(auto_attribs=True)
class _SHandler:
    call_back:Callable[[Message],bool]
    '返回JSON数据\n'\
    '返回bool,指示是否继续传播'
    call_type:str
    '事件类型'
    call_match:dict = {}
    '项与data相匹配,可以是正则表达式'

_handlers:list[_SHandler] = []

def on_message(**match):
    def dect(func:Callable):
        _handlers.append(_SHandler(func,'message',match))
        return func
    return dect

def on_meta_event(**match):
    def dect(func:Callable):
        _handlers.append(_SHandler(func,'meta_event',match))
        return func
    return dect

def on_request(**match):
    def dect(func:Callable):
        _handlers.append(_SHandler(func,'request',match))
        return func
    return dect

def _handle_(data:Message):
    for i in _handlers:
        if i.call_type == data['post_type']:
            enabled = True
            for mem in i.call_match.items():
                if isinstance(mem[1],re.Pattern):
                    if not bool(mem[1].match(data[mem[0]])):
                        enabled = False
                        break
                else:
                    if data[mem[0]] != mem[1]:
                        enabled = False
                        break
            if enabled:
                try:
                    if i.call_back(data) == False:
                        break
                except Exception as e:
                    traceback.print_exception(e)
                    break
            