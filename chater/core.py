"""
Standard Core
"""
from __future__ import annotations
from abc import abstractmethod

from typing import Generator, Generic, TypeVar
import uuid

from .error import *
import attr

_ID = TypeVar('_ID')

class Conversation:
    '''
    Conversation between user and bot
    '''
    def __init__(self,id:_ID,_uuid:uuid.UUID = None) -> None:
        self._uuid:uuid.UUID = _uuid
        self._new_created = True
        self._id:_ID = id
        self._in_bot:Bot = None
        self._conversation_live_time:float = 0
        '''最大对话存活时间,0表示不限制'''
        self._parent_message_id:uuid.UUID = None
        '''父对话ID,开始时为None(ChatGPT需随机生成)'''
        self._chating_user = None
        '''与该机器人对话的User'''
        self._last_available_time:float = None
        '''上一次可利用时间'''
        self._last_request_time:float = None
        '''上一次请求时间'''
        self._deleted:bool = False

    @property
    @abstractmethod
    def on_conversation(self) -> bool:
        pass

    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid

    @property
    def parent_id(self) -> uuid.UUID:
        return self._parent_message_id

    @abstractmethod
    def ask(self,prompt:str) -> Generator[dict]:
        '''Ask Chatbot,Yield Every Generation'''
        pass

    @abstractmethod
    def text(self,prompt:str) -> Generator[str]:
        '''Ask Chatbot,Yield Every Word'''
        pass

    
    def split(self,prompt:str,split:str) -> Generator[str]:
        '''Ask Chatbot,Yield Every Spilted Prompt'''
        curwords:str = ''
        for word in self.text(prompt):
            curwords += word
            if curwords.endswith(split):
                yield curwords[:-len(split)]
                curwords = ''
        yield curwords

    @abstractmethod
    def compeletion(self,prompt:str)->str:
        pass

    @abstractmethod
    def delete(self) -> None:
        if self._deleted:
            raise ConversationNotExisted()
        self._in_bot._conversations.remove(self)
        self._deleted = True

    def __del__(self):
        if not self._deleted:
            self.delete()

class Bot:
    '''
    Chat Bot
    '''
    _con_type:type = Conversation
    def __init__(self,config:dict,id:_ID = None) -> None:
        self._id = id if id else str(uuid.uuid4())
        self._config:dict = config
        self._conversations:list[Conversation] = []
        self._max_on_conversations:int = 1
        '''最大同时对话数'''
        self._conversation_live_time:float = 0
        '''最大对话存活时间,0表示不限制'''

    @property
    def max_on_conversations(self):
        return self._max_on_conversations

    @property
    def conversation_live_time(self):
        return self._conversation_live_time

    @conversation_live_time.setter
    def conversation_live_time(self,value:float):
        self._conversation_live_time = value

    def find_conversation(self,id:_ID):
        for i in self._conversations:
            if i._id == id:
                return i
        return None

    def new_conversation(self,id:_ID = None):
        on_cons:int = 0
        '''正在对话数'''
        if id == None:
            id = str(uuid.uuid4())
        else:
            for i in self._conversations:
                if i.on_conversation:on_cons += 1
                if i._id == id:
                    raise IDExisted(id)
        _toadd = self._con_type(id)
        _toadd._in_bot = self
        self._conversations.append(_toadd)
        return _toadd

    def find_cre_conversation(self,id:_ID):
        ret = self.find_conversation(id)
        if ret:return ret
        return self.new_conversation(id)

_GR = TypeVar('_GR')
class Group(Generic[_GR]):
    def __init__(self,id:_ID = None) -> None:
        super().__init__()
        self._id = id if id else uuid.uuid4()
        self._members:list[_GR] = []
        self.__iter__ = self._members.__iter__

    def find(self,id:_ID) -> _GR | None:
        for i in self._members:
            if i.id == id:
                return i
        return None

    def add(self,member:_GR) -> None:
        if self.find(member.id):
            raise IDExisted(member.id)
        self._members.append(member)

    def remove(self,id:_ID) -> None:
        tar = self.find(id)
        if tar:
            self._members.remove(tar)
            return
        raise IDNotFound(id)

    __getitem__ = find
    __delitem__ = remove

@attr.s(auto_attribs=True)
class User: 
    id:_ID

@attr.s(auto_attribs=True)
class UserConversation:
    user:User
    conversations:Group[Conversation]

    def find_by_id(self,id:_ID) -> Conversation:
        try:
            return self.conversations[[i.id for i in self.conversations].index(id)]
        except ValueError:
            raise IDNotFound(id)

class Conversations(list[UserConversation]):
    def find_con_id(self,id:_ID) -> Conversation | None:
        for i in super():
            for j in i.conversations:
                if j._id == id:
                    return j
