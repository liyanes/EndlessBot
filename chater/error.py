from .core import _ID,Conversation
class BaseException(Exception):
    '''ChatBot Base Execption'''

class IDExisted(BaseException):
    '''ID已经存在'''
    def __init__(self, id:_ID,*args: object) -> None:
        super().__init__(*args)
        self.id = id

class IDNotFound(BaseException):
    '''ID不存在'''
    def __init__(self, id:_ID,*args: object) -> None:
        super().__init__(*args)
        self.id = id


class OnBusy(BaseException):
    '''机器人繁忙'''
    def __init__(self, conversion:Conversation,*args: object) -> None:
        super().__init__(*args)
        self.conversion = conversion

class TooManyRequests(BaseException):
    '''请求过于频繁'''
    def __init__(self, conversion:Conversation | None = None, *args: object) -> None:
        super().__init__(*args)
        self.conversion = conversion

class NetWorkException(BaseException):
    '''网络问题'''

class ConfigureException(BaseException):
    '''配置错误'''
    def __init__(self,config:dict,*args: object) -> None:
        super().__init__(*args)
        self.config = config

class LoginFailed(BaseException):
    '''登录失败'''
    def __init__(self,login_info:dict,*args: object) -> None:
        super().__init__(*args)
        self.login_info = login_info

class ConversationNotExisted(BaseException):
    '''对话不存在'''

class DeleteFailed(BaseException):
    '''删除失败'''

class GenerateFail(BaseException):
    '''机器人生成失败'''
    def __init__(self, conversation:Conversation,*args: object) -> None:
        super().__init__(*args)
        self.conversation = conversation


