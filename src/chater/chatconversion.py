from typing import Any, Iterable
import attr
from . import error,core
import json
import requests
import os

# 可选API Key:pk-TNkDYMHpJKKuSfiAWJlUCKQSnKluoZxvLGKRPnPzxCDPdVxs

class Records:
    '''对话记录'''
    def __init__(self,auto_limit:int = 10) -> None:
        self._records:list[tuple(str,str)] = []
        '''对话记录,前一个是role,后一个是content'''
        self.system_prompt:str = ""
        self._limit = auto_limit
    
    def add_record(self,role:str,content:str):
        self._records.append((role,content))
        if len(self._records) > self._limit:
            self._records.pop(0)

    def generate(self):
        return [
            {'role':'system','content':self.system_prompt},
            *[{'role':i[0],'content':i[1]} for i in self._records]]

@attr.s(auto_attribs=True)
class User:
    id:str
    inform:dict = {}

Model = str

@attr.s(auto_attribs=True)
class SpawnParameter:
    model:Model = 'gpt-3.5-turbo-0301'
    '''模型ID'''
    temperature:float = 1.0
    '''随机度,0-2之间'''
    top_p:float = 1.0
    '''采样率,只有头百分之top_p的tokens会被考虑'''
    n:int = 1
    '''生成的消息数'''
    # stream:bool = False
    # '''流式消息传输,若为True,则像ChatGPT返回消息片段,False则完整返回'''
    stop:bool | Iterable[bool] | None = None
    '''指示是否暂停?'''
    max_tokens:int|None = None
    '''最大生成tokens数,None表示模型最高限制'''
    presence_penalty:float = 0.0
    '''-2到2,表示对讨论新主题的倾向'''
    frequency_penalty:float = 0.0
    '''-2到2,对生成的重复tokens进行惩罚,以减少重复行的可能性'''
    logit_bias:int | None = None
    '''-100到100,表示tokens生成偏差'''
    user:Any = None
    '''用户标识符,用于监视滥用情况'''

    def to_dict(self):
        ret = {'model':self.model}
        if self.temperature != 1.0:ret['temperature'] = self.temperature
        if self.top_p != 1.0:ret['top_p'] = self.top_p
        if self.n != 1:ret['n'] = self.n
        if self.stop != None:ret['stop'] = self.stop
        if self.max_tokens != None:ret['max_tokens'] = self.max_tokens
        if self.presence_penalty != 0.0:ret['presence_penalty'] = self.presence_penalty
        if self.frequency_penalty != 0.0:ret['frequency_penalty'] = self.frequency_penalty
        if self.logit_bias != None:ret['logit_bias'] = self.logit_bias
        if self.user != None:ret['user'] = self.user
        return ret

class Conversation:
    def __init__(self,user:User,system_prompt:str = '',proxy:dict|None = None) -> None:
        self.spawn_param = SpawnParameter()
        self.user = user
        self.records = Records()
        self.records.system_prompt = system_prompt
        self.api_key:str = ''
        # self.session = aiohttp.ClientSession('https://api.openai.com/')
        self.session:requests.Session = requests.session()
        if proxy:
            self.session.proxies.update(proxy)
    
    def completition(self,prompt:str,norecord:bool = False):
        tosend = self.spawn_param.to_dict()
        # Stream False
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Authorization'] = f'Bearer {self.api_key}'
        messages = self.records.generate()
        messages.append({'role':'user','content':prompt})
        tosend['messages'] = messages
        self.records.add_record('user',prompt)
        try:
            with self.session.post('https://api.openai.com/v1/chat/completions',json=tosend) as res:
                if res.status_code != 200:
                    raise error.NetReturnError(self,res)
                content = json.loads(res.content)
                if not norecord:
                    self.records.add_record('assistant',content['choices'][0]['message']['content'])
                return content
        except requests.exceptions.Timeout as e:
            raise error.Timeout(self,e)
        except requests.exceptions.ProxyError as e:
            raise error.ProxyError(self,e)
        except requests.exceptions.ConnectionError as e:
            raise error.ConnectionError(self,e)

class Bot:
    def __init__(self,system_prompt:str = '',api_key:str = '',proxy:dict|None = None) -> None:
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.conversations:list[Conversation] = []
        self.default_param = SpawnParameter()
        self.proxy = proxy or os.environ.get('http_proxy')

    def find_conversation(self,user:User):
        for i in self.conversations:
            if i.user == user:
                return i
            
    def new_conversation(self,user:User):
        '''如果存在,将删除原有对话'''
        src = self.find_conversation(user)
        if src:
            self.conversations.remove(src)
        
        newc = Conversation(user,self.system_prompt)
        newc.api_key = self.api_key
        newc.spawn_param = self.default_param

        self.conversations.append(newc)
        return newc
    
    def get_conversation(self,user:User):
        '''获取对话信息,如果没有则创建对话'''
        src = self.find_conversation(user)
        if src:return src
        return self.new_conversation(user)
    
    def remove_conversation(self,user:User):
        src = self.find_conversation(user)
        if src:
            self.conversations.remove(src)
            return True
        return False