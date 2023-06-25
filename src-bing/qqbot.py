'''
QQ 机器人
'''

import asyncio
import logging
import os
import re
import time
import traceback

import EdgeGPT as eg
import cqmoudle as cq

PROXY = 'http://localhost:10809'

enterpoint = cq.Enterpoint()
manager:dict = {
    'message_type':'private',
    'sub_type':'friend',
    'user_id':...
}

# enterpoint = cq.Enterpoint()
bot_on:bool = True

manager['user_id'] = 3471987674

bots:dict[int,eg.Chatbot] = {}
bot_create_time:dict[int,float] = {}

friend_requests:list[cq.Message] = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

async def init():
    logger.info("正在启动")
    await enterpoint.start()

@enterpoint.on_message(message_type='private',sub_type='friend')
async def _f_mark_read( message:cq.Message):
    try:
        await message.mark_read()
    except:
        logger.warning("标记已读失败")
    return True

@enterpoint.on_message(**manager,message=re.compile('^/.*$'))
async def _f_cmd( message:cq.Message):
    logger.debug('[cmd]收到命令:' + message['message'])
    return True

@enterpoint.on_message(**manager,message=re.compile('^/start *$'))
async def _f_cmd_start(message:cq.Message):
    bot_on = True
    logger.info("[cmd]机器人已启动")
    await message.send('机器人已启动')
    return False

@enterpoint.on_message(**manager,message=re.compile('^/stop *$'))
async def _f_cmd_stop(message:cq.Message):
    bot_on = False
    logger.info("[cmd]机器人已停止")
    await message.send('机器人已停止')
    return False

@enterpoint.on_message(**manager,message=re.compile('^/status *$'))
async def _f_cmd_status(message:cq.Message):
    await message.send('机器人正在运行' if bot_on else '机器人停止运行')
    logger.debug('[cmd]机器人状态查询,当前状态' + ('运行' if bot_on else '停止'))
    return False

@enterpoint.on_message(**manager,message=re.compile('^/help *$'))
async def _f_cmd_help( message:cq.Message):
    await message.send('命令:\nhelp\nlist\nstatus\nstart\nstop\nreset\nresetall')
    return False

@enterpoint.on_message(message_type='private',sub_type='friend',message='/reset')
async def _f_reset(message:cq.Message):
    if bot_on:
        if message.user_id in bots:
            del bots[message.user_id]
        await message.send('已重置')
    return False

@enterpoint.on_request(request_type='friend',)
async def _f_req_friend( message:cq.Message):
    friend_requests.append(message)
    await enterpoint.send(manager['user_id'],f'收到好友请求\n{str(message["user_id"])}\n{message["comment"]}')
    return False

@enterpoint.on_message(**manager,message=re.compile('^/friend( .*|)$'))
async def _f_cmd_friend( message:cq.Message):
    if re.compile(r'/friend( .*|)$').match(message['message']) == None:
        return True
    msg:str = message['message']
    if re.compile(r'^/friend( *)$').match(msg):
        await message.send('当前好友列表:\n' + '\n'.join([str(i) for i in await enterpoint.get_friend_list()]))
        logger.debug('[cmd]好友列表查询')
        return False
    if re.compile(r'^/friend add (\d+)$').match(msg):
        qq = re.compile(r'^/friend add (\d+)$').match(msg).group(1)
        qq = int(qq)
        if qq in [i['user_id'] for i in await enterpoint.get_friend_list()]:
            await message.send('该用户已经是你的好友')
            return False
        for i in friend_requests:
            if i['user_id'] == qq:
                i.accept()
                friend_requests.remove(i)
                await message.send('添加成功')
                logger.info('[cmd]添加好友:' + str(qq))
                return False
        await message.send('未找到该用户的好友请求')
        return False
    if re.compile(r'^/friend remove (\d+)$').match(msg):
        qq = re.compile(r'^/friend remove (\d+)$').match(msg).group(1)
        qq = int(qq)
        if qq in [i['user_id'] for i in await enterpoint.get_friend_list()]:
            await message.delete_friend(qq)
            await message.send('删除成功')
            logger.info('[cmd]删除好友:' + str(qq))
            return False
        await message.send('该用户不是你的好友')
        return False
    if re.compile(r'^/friend requests$').match(msg):
        await message.send('好友请求列表:\n' + '\n'.join([f'{i["user_id"]}\n{i["comment"]}' for i in friend_requests]))
        logger.debug('[cmd]好友请求列表查询')
        return False
    await message.send('命令:\nfriend\nfriend add <qq>\nfriend remove <qq>\nfriend requests')
    return False
    
def _generate_messgae(response:dict):
    messages = response['item']['messages']
    messages = [i['text'] for i in messages if 'text' in i and i['author'] == 'bot']
    return '\n\n'.join(messages)

def _generate_quote(response:dict):
    use_num = response['item']['throttling']['numUserMessagesInConversation']
    max_num = response['item']['throttling']['maxNumUserMessagesInConversation']
    quotes_set = [i for i in response['item']['messages'] if 'sourceAttributions' in i]
    quotes = []
    for i in quotes_set:
        quotes += i['sourceAttributions']
    if len(quotes) > 0:
        quote_text = '\n'.join(
            f"[{i+1}]{quote['providerDisplayName']} - {quote['seeMoreUrl']}" for i, quote in enumerate(quotes)
        )
        return f"已使用{use_num}/{max_num}\n引用至:{quote_text}"
    return f"已使用{use_num}/{max_num}"

def _check_usable( response:dict):
    use_num = response['item']['throttling']['numUserMessagesInConversation']
    max_num = response['item']['throttling']['maxNumUserMessagesInConversation']
    return use_num < max_num

def _check_expired( user_id:int):
    return bot_create_time[user_id] + 60 * 60 * 3 < time.time()

def _get_bot( user_id:int):
    if user_id in bots:
        if not _check_expired(user_id):
            return bots[user_id]
    bots[user_id] = eg.Chatbot(proxy=PROXY)
    bot_create_time[user_id] = time.time()
    return bots[user_id]

@enterpoint.on_message(message_type='private',sub_type='friend')
async def _f_ask(data:cq.Message):
    if bot_on:
        try:
            logger.info(f'User[{data["user_id"]}]{data["message"]}')
            bot = _get_bot(data.user_id)
            ret = await bot.ask(data['message'],search_result=True,conversation_style=eg.ConversationStyle.creative)
            if not _check_usable(ret):
                del bots[data.user_id]
            to_send = _generate_messgae(ret).split('\n\n')
            for i in to_send:
                await data.send(i)
            await data.send(_generate_quote(ret))
            logger.info(f"-> User[{data['user_id']}]" + _generate_messgae(ret))
        except Exception as e:
            await data.send('[error]发生了错误, 请稍后再问, 如果持续错误, 请联系开发者, 该对话将被重置')
            del bots[data.user_id]
            logger.error('\n'.join(traceback.format_exception(e)))
    return False

@enterpoint.on_message(message_type='group',sub_type='normal')
async def _f_ask_group( data:cq.Message):
    if bot_on:
        try:
            if not data['message'].startwiths('chat '):
                return False
            data['message'] = data['message'][5:]
            bot = await bots[data.user_id] if data.user_id in bots else eg.Chatbot(proxy=PROXY)
            logger.info(f'Group[{data["group_id"]}][{data["user_id"]}]{data["message"]}')
            ret = await bot.ask(data['message'],search_result=True)
            if not _check_usable(ret):
                del bots[data.user_id]
            to_send = _generate_messgae(ret).split('\n\n')
            for i in to_send:
                await data.send(i)
            await data.send(_generate_quote(ret))
            logger.info(f"-> Group[{data['group_id']}][{data['user_id']}]" + _generate_messgae(ret))
        except Exception as e:
            await data.send('[error]发生了错误, 请稍后再问, 如果持续错误, 请联系开发者, 该对话将被重置')
            del bots[data.user_id]
            logger.error('\n'.join(traceback.format_exception(e)))
    return False
    
async def final():
    await enterpoint.close()

async def main():
    await init()

loop = asyncio.new_event_loop()
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
try:
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    loop.stop()
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.run_forever()
    loop.stop()
    loop.close()
