import os
import re
import traceback
import qqhandler
from qqhandler import Message
import chater
import attr
import sys
import logging
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv(os.path.join(os.path.dirname(sys.argv[0]),'.env'))

log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)

log_for = logging.Formatter('[%(asctime)s] %(levelname)s : %(message)s')

fil = logging.FileHandler('qqbot.log')
fil.encoding = 'utf8'
col = logging.StreamHandler()

fil.setFormatter(log_for)
col.setFormatter(log_for)

fil.setLevel(getattr(logging,os.environ.get('LOG_LEVEL')) if os.environ.get('LOG_LEVEL') else logging.WARNING)
col.setLevel(getattr(logging,os.environ.get('CONSOLE_LOG_LEVEL')) if os.environ.get('CONSOLE_LOG_LEVEL') else logging.INFO)

if os.environ.get('ENABLE_LOG') == '1':
    log.addHandler(fil)
log.addHandler(col)

bot = chater.ChatConversation.Bot(
    'You are ChatGPT,a launage model developed by OpenAI.\n'
    'In this conversation, you will be playing the role of an AI assistant.\n'
    'You will have a conversation with a human via this assistant.\n'
    ,
    os.environ.get('API_KEY')
)
if os.environ.get('PROXY'):
    bot.proxy = {
        'http':os.environ.get('PROXY'),
        'https':os.environ.get('PROXY')
    }

log.info("机器人初始化完成")

bot_on:bool = True

enable_white:bool = False
'''
启用白名单,否则黑名单
'''

white_list:list[str] = []
black_list:list[str] = []

group_white_list:list[str] = []

################### 名单管理文件 ###################

if os.path.exists('white.list'):
    with open('white.list','r',encoding='utf8') as f:
        white_list = f.read().splitlines()

if os.path.exists('black.list'):
    with open('black.list','r',encoding='utf8') as f:
        black_list = f.read().splitlines()

if os.path.exists('group_white.list'):
    with open('group_white.list','r',encoding='utf8') as f:
        group_white_list = f.read().splitlines()

def add_white_list(user_id:str):
    if user_id not in white_list:
        white_list.append(user_id)
        with open('white.list','a',encoding='utf8') as f:
            f.write(user_id + '\n')

def add_black_list(user_id:str):
    if user_id not in black_list:
        black_list.append(user_id)
        with open('black.list','a',encoding='utf8') as f:
            f.write(user_id + '\n')

def add_group_white_list(group_id:str):
    if group_id not in group_white_list:
        group_white_list.append(group_id)
        with open('group_white.list','a',encoding='utf8') as f:
            f.write(group_id + '\n')

def remove_white_list(user_id:str):
    if user_id in white_list:
        white_list.remove(user_id)
        with open('white.list','w',encoding='utf8') as f:
            f.write('\n'.join(white_list))

def remove_black_list(user_id:str):
    if user_id in black_list:
        black_list.remove(user_id)
        with open('black.list','w',encoding='utf8') as f:
            f.write('\n'.join(black_list))

def remove_group_white_list(group_id:str):
    if group_id in group_white_list:
        group_white_list.remove(group_id)
        with open('group_white.list','w',encoding='utf8') as f:
            f.write('\n'.join(group_white_list))

################### 消息处理区 ###################

manager:dict = {
    'message_type':'private',
    'sub_type':'friend',
    'user_id':int(os.environ['MANAGER_ID'])
}

@qqhandler.on_message(message_type='private',sub_type='friend')
def mark_read(data:Message):
    try:
        data.mark_read()
    except:
        log.warning("标记已读失败")
    return True


################# 命令区 #################
@qqhandler.on_message(**manager,message=re.compile('^/.*$'))
def cmd(data:Message):
    log.debug('[cmd]收到命令:' + data['message'])
    return True

@qqhandler.on_message(**manager,message=re.compile('^/start *$'))
def cmd_start(data:Message):
    global bot_on
    bot_on = True
    log.info("[cmd]机器人已启动")
    data.mark_read()
    data.send('机器人已启动')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/stop *$'))
def cmd_stop(data:Message):
    global bot_on
    bot_on = False
    log.info("[cmd]机器人已停止")
    data.mark_read()
    data.send('机器人已停止')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/status *$'))
def cmd_status(data:Message):
    data.mark_read()
    data.send('机器人正在运行' if bot_on else '机器人停止运行')
    log.debug('[cmd]机器人状态查询,当前状态' + ('运行' if bot_on else '停止'))
    return False

@qqhandler.on_message(**manager,message=re.compile('^/list(.*)?$'))
def cmd_list(data:Message):
    if re.compile(r'/list( .*|)$').match(data['message']) == None:
        return True
    msg:str = data['message']
    if re.compile(r'^/list( *)$').match(msg):
        data.send('白名单:\n' + '\n'.join(white_list) + '\n黑名单:\n' + '\n'.join(black_list))
    elif re.compile(r'^/list white( *)$').match(msg):
        data.send('白名单:\n' + '\n'.join(white_list))
    elif re.compile(r'^/list black( *)$').match(msg):
        data.send('黑名单:\n' + '\n'.join(black_list))
    elif re.compile(r'^/list white add (\d+)$').match(msg):
        qq = re.compile(r'^/list white add (\d+)$').match(msg).group(1)
        if qq not in white_list:
            add_white_list(qq)
            data.send('添加成功')
            log.info('[cmd]添加白名单:' + qq)
        else:
            data.send('该用户已在白名单中')
    elif re.compile(r'^/list white remove (\d+)$').match(msg):
        qq = re.compile(r'^/list white remove (\d+)$').match(msg).group(1)
        if qq in white_list:
            remove_white_list(qq)
            data.send('移除成功')
            log.info('[cmd]移除白名单:' + qq)
        else:
            data.send('该用户不在白名单中')
    elif re.compile(r'^/list black add (\d+)$').match(msg):
        qq = re.compile(r'^/list black add (\d+)$').match(msg).group(1)
        if qq not in black_list:
            add_black_list(qq)
            data.send('添加成功')
            log.info('[cmd]添加黑名单:' + qq)
        else:
            data.send('该用户已在黑名单中')
    elif re.compile(r'^/list black remove (\d+)$').match(msg):
        qq = re.compile(r'^/list black remove (\d+)$').match(msg).group(1)
        if qq in black_list:
            remove_black_list(qq)
            data.send('移除成功')
            log.info('[cmd]移除黑名单:' + qq)
        else:
            data.send('该用户不在黑名单中')
    elif re.compile(r'^/list group white( *)$').match(msg):
        data.send('群白名单:\n' + '\n'.join(group_white_list))
    elif re.compile(r'^/list group white add (\d+)$').match(msg):
        group_id = re.compile(r'^/list group white add (\d+)$').match(msg).group(1)
        if group_id not in group_white_list:
            add_group_white_list(group_id)
            data.send('添加成功')
            log.info('[cmd]添加群白名单:' + group_id)
        else:
            data.send('该群已在群白名单中')
    elif re.compile(r'^/list group white remove (\d+)$').match(msg):
        group_id = re.compile(r'^/list group white remove (\d+)$').match(msg).group(1)
        if group_id in group_white_list:
            remove_group_white_list(group_id)
            data.send('移除成功')
            log.info('[cmd]移除群白名单:' + group_id)
        else:
            data.send('该群不在群白名单中')
    else:
        data.send('命令:\nlist\nlist white\nlist black\nlist white add <qq>\nlist white remove <qq>\nlist black add <qq>\nlist black remove <qq>\nlist group white\nlist group white add <group_id>\nlist group white remove <group_id>')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/resetall *$'))
def cmd_resetall(data:Message):
    bot.conversations.clear()
    data.send('已重置')
    log.info('[cmd]已重置')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/help *$'))
def cmd_help(data:Message):
    data.send('命令:\nhelp\nlist\nstatus\nstart\nstop\nreset\nresetall')
    return False

@qqhandler.on_message(message_type='private',sub_type='friend',message='/reset')
def reset(data:Message):
    if enable_white:
        if not str(data['user_id']) in white_list:
            return False
    else:
        if str(data['user_id']) in black_list:
            data.send('[error]你无权限使用该机器人')
            return False
    if bot_on:
        con = bot.find_conversation(chater.ChatConversation.User('user-' + str(data['user_id'])))
        if con != None:
            bot.conversations.remove(con)
        data.send('对话已重置')
        log.info(f"重置用户{data['user_id']}的会话")
    return False

################# 好友请求 ###################
friend_requests:list[Message] = []

@qqhandler.on_request(request_type='friend',)
def req_friend(data:Message):
    friend_requests.append(data)
    qqhandler.send(manager['user_id'],f'收到好友请求\n{str(data["user_id"])}\n{data["comment"]}')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/friend(.*)$'))
def cmd_friend(data:Message):
    if re.compile(r'/friend( .*|)$').match(data['message']) == None:
        return True
    msg:str = data['message']
    if re.compile(r'^/friend( *)$').match(msg):
        data.send('当前好友列表:\n' + '\n'.join([str(i) for i in qqhandler.get_friend_list()]))
        log.debug('[cmd]好友列表查询')
        return False
    if re.compile(r'^/friend add (\d+)$').match(msg):
        qq = re.compile(r'^/friend add (\d+)$').match(msg).group(1)
        if qq in [i['user_id'] for i in qqhandler.get_friend_list()]:
            data.send('该用户已经是你的好友')
            return False
        for i in friend_requests:
            if i['user_id'] == int(qq):
                i.enable_friend()
                friend_requests.remove(i)
                data.send('添加成功')
                log.info('[cmd]添加好友:' + qq)
                return False
        data.send('未找到该用户的好友请求')
        return False
    if re.compile(r'^/friend remove (\d+)$').match(msg):
        qq = re.compile(r'^/friend remove (\d+)$').match(msg).group(1)
        if qq in [i['user_id'] for i in qqhandler.get_friend_list()]:
            qqhandler.delete_friend(qq)
            data.send('删除成功')
            log.info('[cmd]删除好友:' + qq)
            return False
        data.send('该用户不是你的好友')
        return False
    if re.compile(r'^/friend requests$').match(msg):
        data.send('好友请求列表:\n' + '\n'.join([f'{i["user_id"]}\n{i["comment"]}' for i in friend_requests]))
        log.debug('[cmd]好友请求列表查询')
        return False
    data.send('命令:\nfriend\nfriend add <qq>\nfriend remove <qq>\nfriend requests')
    return False

@qqhandler.on_message(**manager,message=re.compile('^/.*$'))
def cmd_(data:Message):
    msg:str = data['message']
    log.error("[cmd]未知指令:" + msg)
    data.send('未知执行,请查询/help查看所有指令')
    return False

################ 命令区结束 #################

@qqhandler.on_message(message_type='private',sub_type='friend')
def ask(data:Message):
    if enable_white:
        if not str(data['user_id']) in white_list:
            return False
    else:
        if str(data['user_id']) in black_list:
            data.send('[error]你无权限使用该机器人')
            return False
        
    if bot_on:
        con = bot.get_conversation(chater.ChatConversation.User('user-' + str(data['user_id'])))
        log.info(f'[user {data["user_id"]}]{data["message"]}')
        try:
            ret = con.completition(data['message'])
            data.send(ret['choices'][0]['message']['content'])
            log.info(f"-> user {data['user_id']}" + ret['choices'][0]['message']['content'])
        except chater.error.NetReturnError as e:
            data.send('[error]API返回错误,消息体:' + e.response.text)
            log.error('\n'.join(traceback.format_exception(e)) + f'\n{e.response.text}')
        except chater.error.ProxyError as e:
            data.send('[error]代理发送错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.Timeout as e:
            data.send('[error]请求超时,如果多次发生,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.ConnectionError as e:
            data.send('[error]网络连接错误,请再次尝试,如果多次失败,请尝试联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.BaseException as e:
            data.send('[error]返回错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except Exception as e:
            data.send('[error]未知错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
    return False

@qqhandler.on_message(message_type='group',sub_type='normal')
def ask_group(data:Message):
    msg=str(data['message'])
    if not msg.startswith('chat '):
        return False
    if not str(data['group_id']) in group_white_list:
        return False
    if bot_on:
        con = bot.get_conversation(chater.ChatConversation.Group('group-' + str(data['group_id'])))
        log.info(f'[group {data["group_id"]}]{data["message"]}')
        try:
            ret = con.completition(msg[5:])
            data.send(ret['choices'][0]['message']['content'])
            log.info(f"-> group {data['group_id']}" + ret['choices'][0]['message']['content'])
        except chater.error.NetReturnError as e:
            data.send('[error]API返回错误,消息体:' + e.response.text)
            log.error('\n'.join(traceback.format_exception(e)) + f'\n{e.response.text}')
        except chater.error.ProxyError as e:
            data.send('[error]代理发送错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.Timeout as e:
            data.send('[error]请求超时,如果多次发生,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.ConnectionError as e:
            data.send('[error]网络连接错误,请再次尝试,如果多次失败,请尝试联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except chater.error.BaseException as e:
            data.send('[error]返回错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))
        except Exception as e:
            data.send('[error]未知错误,请联系开发者')
            log.error('\n'.join(traceback.format_exception(e)))

qqhandler.start_handler()
