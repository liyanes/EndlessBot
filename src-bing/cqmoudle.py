import asyncio
import re
import traceback
from typing import Callable, Coroutine, Literal

import aiohttp
import attr
from aiohttp import web

RECEIVE_PORT = 5701
UPLOAD_URL = 'http://localhost:5700'

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
    
    async def send(self,message:str) -> int:
        if self.type == 'message':
            if self['message_type'] == 'private':
                await self._send_private(message)
                return self['user_id']
            elif self['message_type'] == 'group':
                await self._send_group(message)
                return self['group_id']
        raise Exception("不支持的消息类型")
    
    async def _send_private(self,message:str):
        async with aiohttp.ClientSession() as client:
            async with client.post(f"{UPLOAD_URL}/send_private_msg",params={
                'user_id':self['user_id'],
                'message':message
                }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()
        
    async def _send_group(self,message:str):
        async with aiohttp.ClientSession() as client:
            async with client.post(f"{UPLOAD_URL}/send_group_msg",params={
                'group_id':self['group_id'],
                'message':message
            }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()

    async def mark_read(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(f'{UPLOAD_URL}/mark_msg_as_read',params={
                'message_id':self['message_id']
            }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()
    
    async def accept(self) -> int:
        if self.type == 'request':
            if self['request_type'] == 'friend':
                await self._enable_friend()
                return self['user_id']
            elif self['request_type'] == 'group':
                await self._enable_group()
                return self['group_id']
        raise Exception("不支持的消息类型")

    async def _enable_friend(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(f'{UPLOAD_URL}/set_friend_add_request',params={
                'flag':self['flag'],
                'approve':True
            }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()
        
    async def _enable_group(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(f'{UPLOAD_URL}/set_group_add_request',params={
                'flag':self['flag'],
                'approve':True,
                'type':'invite'
            }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()
        
    async def delete_friend(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(f'{UPLOAD_URL}/delete_friend',params={
                'user_id':self['user_id']
            }) as res:
                if not res.ok:
                    raise Exception("状态错误")
                return await res.json()


@attr.s(auto_attribs=True)
class _SHandler:
    call_back:Callable[[Message],Coroutine[None,None,bool]]
    '返回JSON数据\n'\
    '返回bool,指示是否继续传播'
    call_type:str
    '事件类型'
    call_match:dict = {}
    '项与data相匹配,可以是正则表达式'

class Enterpoint:
    '''
    入口
    '''
    def __init__(self, upload_url: str = UPLOAD_URL, receive_port: int = RECEIVE_PORT):
        self._session = aiohttp.ClientSession()
        self._server = web.Application()
        self._server.add_routes([web.post('/', self._receive)])
        self._handlers:list[_SHandler] = []
        self._upload_url = upload_url
        self._receive_port = receive_port

    async def start(self):
        await asyncio.get_event_loop().create_server(self._server.make_handler(), 'localhost', self._receive_port)

    async def _receive(self, request: web.Request):
        data = await request.json()
        asyncio.get_event_loop().create_task(self._handle(data))
        return web.json_response()

    def on_message(self,**match):
        def dect(func:Callable):
            self._handlers.append(_SHandler(func,'message',match))
            return func
        return dect

    def on_meta_event(self,**match):
        def dect(func:Callable):
            self._handlers.append(_SHandler(func,'meta_event',match))
            return func
        return dect

    def on_request(self,**match):
        def dect(func:Callable):
            self._handlers.append(_SHandler(func,'request',match))
            return func
        return dect
    
    async def send(self, user:int, message:str):
        async with self._session.post(f"{self._upload_url}/send_private_msg",params={
            'user_id':user,
            'message':message
        }) as res:
            if not res.ok:
                raise Exception("状态错误")
            return await res.json()
        
    async def get_friend_list(self):
        async with self._session.get(f"{self._upload_url}/get_friend_list") as res:
            if not res.ok:
                raise Exception("状态错误")
            return await res.json()['data']
        
    async def close(self):
        await self._server.shutdown()
        await self._server.cleanup()

    async def _handle(self,data:dict):
        for i in self._handlers:
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
                        if (await i.call_back(Message(data))) == False:
                            break
                    except Exception as e:
                        traceback.print_exception(e)
                        break
