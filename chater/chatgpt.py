from __future__ import annotations
from typing import Callable
from .core import *
from . import core
import os
if os.name == 'nt':
    from OpenAIAuth import Authenticator as OpenAIAuth
else:
    from OpenAIAuth.OpenAIAuth import OpenAIAuth
import time
import requests
import json
import warnings
from .error import *
import threading

BASEURL = 'https://chatgpt.duti.tech/'

class ChatGPTConversation(Conversation):
    timeout:int = 500
    def __init__(self, id: core._ID, _uuid: uuid.UUID = None) -> None:
        super().__init__(id, _uuid)
        self._par_message_his:list[uuid.UUID] = []
        self._con_his:list[uuid.UUID] = []
        self._con_id:uuid.UUID = None
        self._in_bot:ChatGPTBot = self._in_bot
        self._on_conversation = False

    @property
    def on_conversation(self) -> bool:
        return self._on_conversation
    
    def ask(self,prompt:str):
        if self._new_created:
            self._parent_message_id = uuid.uuid4()
        data = {
            'action':'next',
            'messages':[{
                'id':str(uuid.uuid4()),
                'role':'user',
                'content':{
                    'content_type':'text',
                    'parts':[
                        str(prompt)
                    ]
                }
            }],
            'conversation_id':str(self._con_id) if self._con_id else None,
            'parent_message_id':str(self._parent_message_id),
            'model': self._in_bot._model
        }
        res = self._in_bot._session.post(
            url = BASEURL + 'api/conversation',
            data = json.dumps(data),
            timeout = self.timeout,
            stream = True
        )
        if res.status_code != 200:
            if self._new_created:
                self.delete()
            raise NetWorkException(res)
        self._on_conversation = True
        first_yield = True
        try:
            for line in res.iter_lines():
                line = str(line)[2:-1]      # 去掉 b\
                
                if line == '' or line == None:
                    continue
                elif line.startswith('data: '):
                    line = line[6:]
                elif line == 'DONE':
                    break

                line = line.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")

                try:
                    data:dict = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                if len(data) == 1:
                    if 'detail' in data:
                        if self._new_created:
                            self.delete()
                        if data['detail'].startswith('Too many requests'):
                            # 请求太频繁
                            raise TooManyRequests(self,prompt,data['detail'])
                        elif data['detail'].startswith('Only one'):
                            # 请求只能有一次
                            raise OnBusy(self,prompt,data['detail'])
                        else:
                            raise BaseException(self,prompt,data['detail'])

                if first_yield:
                    first_yield = False
                    self._con_his.append(self._con_id)
                    self._par_message_his.append(self._parent_message_id)
                    self._con_id = data['conversation_id']
                    self._parent_message_id = data['message']['id']

                self._new_created = False
                yield data
        except Exception as e:
            self._on_conversation = False
            raise e
        self._on_conversation = False

    def text(self, prompt:str):
        yield_len:int = 0
        old_text:str = ''
        for data in self.ask(prompt):
            new_text:str = data["message"]["content"]["parts"][0]
            if old_text == new_text:continue
            if old_text == new_text[:yield_len]:
                inc:int = len(new_text) - yield_len
                for i in range(-inc,0):
                    yield new_text[i]
                yield_len += inc
                old_text = new_text
            else:
                warnings.warn("Unexcepted Answer:" + new_text)
                old_text = new_text
                yield_len = len(old_text)
                yield new_text

    def compeletion(self, prompt: str) -> str:
        content:str = ''
        for i in self.ask(prompt):
            content:str = i["message"]["content"]["parts"][0]
        return content

    def delete(self):
        if self._deleted:
            raise ConversationNotExisted()
        res = self._in_bot._session.patch(
            url = BASEURL + f'api/conversation/{self._con_id}',
            data = json.dumps({
                'is_visible':False
            })
        )
        if res.status_code != 200:
            raise DeleteFailed(res)

    def gen_title(self):
        res = self._in_bot._session.post(
            url = BASEURL + f"api/conversation/gen_title/{self._con_id}",
            data = json.dumps({
                "message_id": self._parent_message_id,
                "model": self._in_bot._model
            })
        )
        if res.status_code != 200:
            raise GenerateFail(self,res)

    def set_title(self,title:str):
        res = self._in_bot._session.post(
            url = BASEURL + f'api/conversation/{self._con_id}',
            data = json.loads({
                'title':title
            })
        )
        if res.status_code != 200:
            raise NetWorkException(res)
    
class ChatGPTBot(Bot):
    '''ChatGPT机器人'''
    _con_type:type = ChatGPTConversation
    def __init__(self, config: dict, id: core._ID = None) -> None:
        super().__init__(config, id)
        self._session = requests.session()
        if not all([i in ['auth','proxy','model','con_live_time'] for i in config]):
            raise ConfigureException(config,'未知参数')

        config.setdefault('model','text-davinci-002-render-sha')
        self._model = config['model']

        self._conversation_live_time = config.get('con_live_time',0)
        
        if 'proxy' in config:
            if isinstance(config['proxy'],str):
                # 单字符串
                self._session.proxies.update({
                    'http':config['proxy'],
                    'https':config['proxy'],
                })
            elif isinstance(config['proxy'],dict):
                self._session.proxies.update(config['proxy'])
            else:
                raise ConfigureException(config,'未知代理格式')

        self._login(config)
    
    def _login(self,config:dict):
        login_info = config['auth']
        if 'email' in login_info and 'passwd' in login_info:
            def login():
                auth = OpenAIAuth(
                    email_address = login_info['email'],
                    password = login_info['passwd'],
                    proxy = (
                        config['proxy'] if isinstance(config['proxy'],str) else
                            config['proxy']['https']
                    ) if config['proxy'] else None
                )
                try:
                    auth.begin()
                except Exception as e:
                    raise LoginFailed(e)
                self._session_token = auth.session_token
                auth.get_access_token()
                if auth.access_token == None:
                    login()
                self._access_token = auth.access_token
                
            login()
            self._update_headers()
        elif 'session_token' in login_info:
            def session_login():
                auth = OpenAIAuth(
                    email_address = None,
                    password = None,
                    proxy = (
                        config['proxy'] if isinstance(config['proxy'],str) else
                            config['proxy']['https']
                    ) if config['proxy'] else None
                )
                auth.session_token = login_info['session_token']
                auth.get_access_token()
                if auth.access_token == None:
                    session_login()
                self._access_token = auth.access_token
            session_login()
            self._update_headers()
        else:
            raise ConfigureException("Unknown Login Config")

    def _update_headers(self):
        self._session.headers.clear()
        self._session.headers.update({
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
        })

    @property
    def onbusy(self):
        return all([i.on_conversation for i in self._conversations])

@attr.s(auto_attribs=True)
class GPTAsk:
    user:User
    con_id:str
    '''指Conversation的ID'''
    prompt:str
    create_time:float
    call_back:Callable = None
    '''回调函数,将默认含有参数user,prompt,create_time,conversion'''
    call_args:tuple = ()
    call_wargs:dict = {}

class GPTAskQueue(list[GPTAsk]):
    '''GPT询问列表'''
    def __init__(self):
        self._on_not_empty = threading.Event()

    def get(self):
        if len(self):
            if len(self) == 1:self._on_not_empty.clear()
            return super().pop(0)
        return None

    @property
    def not_empty(self):
        return bool(len(self))

    def push(self,gptask:GPTAsk):
        super().append(gptask)
        self._on_not_empty.set()

    def wait(self):
        self._on_not_empty.wait()

class ChatGPTAskQueue:
    def __init__(self,chatGPTBot:ChatGPTBot) -> None:
        self._bot = chatGPTBot
        self._queue = GPTAskQueue()
        
    def handle(self):
        if self._queue.not_empty:
            ask = self._queue.get()
            con = self._bot.find_cre_conversation(ask.con_id)
            ask.call_back(
                user=ask.user,
                prompt=ask.prompt,
                create_time=ask.create_time,
                conversation=con,
                *ask.call_args,
                **ask.call_wargs
            )

    def handle_forever(self,_async:bool = True):
        def handle_all(chatqueue:ChatGPTAskQueue):
            while True:
                if not self._queue.not_empty:
                    chatqueue._queue.wait()
                chatqueue.handle()
        if _async:
            th = threading.Thread(target=handle_all,args=(self,),daemon=True)
            th.start()
        else:
            handle_all()

    def push(self,ask:GPTAsk):
        self._queue.push(ask)
