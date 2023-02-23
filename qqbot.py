from email import message
import os
import re
import traceback
import uuid
import qqunilt
import qqhandler
import time
import chater
import attr

DATA_IMAGE_PATH:str = 'D:\Programs\cqhttp\data\images'

# ########### LaTex数据处理 ############
# 废弃

# @attr.s(auto_attribs=True)
# class MathImageMap:
#     file:str
#     uid:str
#     src_latex:str

# class MathImageMaps(list[MathImageMap]):
#     def delete_by_uid(self,uid:str):
#         for i in self:
#             if i.uid == uid:
#                 os.remove(os.path.join(DATA_IMAGE_PATH,i.file))
#                 super().remove(i)

#     def handle_res(self,string:str,uid:str):
#         '''处理字符串,将其中的LaTex表达式转化为图片'''
        
#         def gener_latex_image(latex:str,path:str):
#             mt.math_to_image(latex,path,dpi=72,prop=fm.FontProperties(
#                 size=30,weight='normal'
#             ))
        
#         import re
#         val = re.compile('\$\$(.*?)\$\$').sub(lambda mac:f"\n${mac.group(1)}$\n",string)
#         def handle_single(match:re.Match):
#             ma = MathImageMap(str(uuid.uuid4()) + '.png',uid,match.group(0))
#             gener_latex_image(match.group(0),os.path.join(DATA_IMAGE_PATH,ma.file))
#             self.append(ma)
#             return f'[CQ:image,file={ma.file}]'
#         return re.compile('\$(.*?)\$').sub(handle_single,val)

# mi_maps:MathImageMaps = MathImageMaps()
# ############# LaTex处理结束 ##############

bot = chater.ChatGPTBot({
    'auth':{
        'session_token':'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..ybR17R18-c5uXhqt.EJKcT_7gfPaytoVJsd7-HD2jPEYitwRDcSd7Kgq-8jRz-gWXed2DJ-3QNn6SQjjVUjC4x9mPHd-91x9V3hylUv1Wb3XY6UYCQPdaDYn6Fw19IL8BPMo21QdHZ5osnAs3_grGKoRrYsI5EqLK-QzXueYLLuD4tMt-KpVeijsNCtlknDcwTnqowYS8wQPj5wY9N31RAFmi2_yQMGUtwMusujFACMcCl8VhrHfiCJXx8dBFvAih3AsGHnV630kauMWUwsqe3ka5tlRf95di-MpMsn6eR9KtU9UwVGI4CvhAafF4EOBkpGhLk3C4kmS_YyMqkoFBytvS9lg7cJYQKUOjEZ_ylJpZIqZmqJ1Rs3XRMa41C86WCuUYfDesKDvePm9s7fkP0nVks6rZTbIJqejakLAtPR3-0vUigz_kT5awV_omdpNmkk3xtYuWIysVLWLAmQ-70FSiuxHbCy4kRQxBUSHTYUYzB1paqMjkb2u4bvLHPQuhgXGq3dssiBtPgDT-aqfy7HouHnd4yb6dtkXMYWwxMRuhOF7X2CwfVlBndHIAFgjn0roX1yO_egI74gpikvk4epCr-Tm1dZs4RbJmKKs9v9Nw3kvqakUEqjcdfcW0BfDfLZ4IaTzqnUn7OZZtC6x8Jnjr7SU_Talpg0RxF4mKncEFhjjQ2Q7-XQGaM8iV61PI_A4O19rL4ZNCqohzdmLE8t62lN8Aou0VUVKO0YQ41PHYPt2i18bsT4NpQWt2zKbMTVr1DOgwtBrm0QIg_tK9fpKGuZPtVknlviymRK1bIR2c9FbuiqMxGhpeKFsNg3GPCn3oIPJOIam9DMHHJUbQJqg1HByyqOtinJiedzzIWmHkfg9O464zgU4bY4tj9TcCOjmfRph-rPyVJP6shFBUhP15sOVb5ZtVK-HAz9Hpf2qWi46e8OrQkqo6jcVQnQkvc16Qbu_8l7Yw25v1MzCvDF0s7r6-ekjeoAtsWHx6s7pxB36GoRsxC56a0qhwBYy_Xijw3KqsXtB-h-L9_fYx5uw5jAod4e6V0gBiPvP-sldQOIaub31VUENt-QDbTrbvt_yKMjL7_25UDERkZgheglT-B2UbUcceRrCwphgqQFGGzNDrkaP7m0KfbxOulgYvE48lvIOFMoz3KESMmGBd1qNoj1UwBTtpGhAuOxQ3OZTkloR0C8Xz8qsUX3pcg-mP87ldU2EUgppaJG4ZIJHeMh6L3lNZNBQwh5RUmkOUDy8zx-HELikvEsjO9GGKrMwUkqTamN674YKvfrBMEZL0Vx49ijVYbqw5kgGGqa7IYOKhJJJLrpaOQlPal25NhHBgzn13feazcs4imTNcP78JTD3IE3SmEqM4ZoXkK7Dj-mIY-FKZ0Zrrq3DZGi2Vcf0whBlYOsbagLh42JD3baRk5GYBRDNsN1NF0q5_CtgkkftR0fyANpmKca-svDhn26TpYWsT0aD0M5aTx4es92zOSvnOyopuJhgEnqjugMYPCGWniK82rDNzI2QuHVbPPrAiqFUY0uoGNof_TrMI18C5xnnL1YLb25S_G2bFl8c_qIZN0p5ekxCRLRdR1WyoEKgk-xTL4nkxry9NyxkwXuk8GXAmM3VS-M-90oUGcw7eT5xABa5z3r9o75t7tRShlev_0VGC3qN5TtAkJnjFIZyKUyRDVfp3XRfzpwGkfB7EeoEClDmjptwUDCv_FRZC_NDeWAzbUidHPg2zExijIBrD1Pwf4RzZ4hzhYoe1SMDuuvGcu0hRzaJSuU47vQ04PfBX7Wy795jlTyvbHsY6wi4ijRHcDoR0bXpaeYnmbaCtuv68F-A8NGj7byF4eIQYTpC0IrlnudxHn3NKfQLvtSp6cCc9_RfsUrzrGq7bhBBHkbdBGVMjXjuw4HjalNLVMJfxWL_YftKJ7YwyAAKPK2IFlp8lWXh1JX-NiGn5IDYRFtUdGgFp6uLNf945ToGdmAJBNKfwQ9fg-iM0tNU-TLm6VyPDevW94hE3pdHsXWcJxMCWyoX_iyJj_aD47LO_5XpziWhQ9iVGJN8TLbDhFyR4LNmemk2d6DZTA332495o3-4rmTrHGytjuCmK7y50cH2hN4fjPXazMj6XdLGs_VaA3sQ9qp1T6p3-PrE-5Kcydg-lFIKQSDjt4asKWpUnOmUikQZHS65Z4dgnqUSZgRiLSDjvrthzzEZ9L88RLvbs9ExKomkuFOko2f-bt_KCxfE2mwcbd27i2F1alGtclJyDSmJZKJLX3NNStYTbVLkCGiIS23oKQmBu6WsOEpyQrpRLnXYy7198pRz3uILpLFfbiANBTuHq97itud5yKeSJgKpqEdOXRJaHV1AWlqYrzk77cND05-i1aI42JnHNGfis4KdTZvcW07wmdn6uOTDWVPr6lgIM1xXne3XjUyjJrQjLlAw8nupr-j5hKXinNxGt1MElGfRb2mHnQmIvajGt17s5QxVo5u4udx9spjhab-SxRlpfFAeZWiwzE8utuQpJm7CxJ7T-SKqsmVhXIrMxHi7LGO-xCBT28BTT_oI4azMcc_PDMDCEic6nB3J66yluMKA0dM1aix-_sE9RQc7S62r1XogympALEYh1NO6ave05e2Ohg1vZpQkj22dmaXB3Ojlnojb4eRoW.mACx8KupcLj8xFDM9Sq_TQ'
    },
    'proxy':'http://localhost:10809'
})

que = chater.ChatGPTAskQueue(bot)

print("机器人初始化完成")

bot_on:bool = True

@qqunilt.on_message(message_type='private',sub_type='friend',user_id=3471987674,message=re.compile('/.*'))
def command_check(data:dict):
    global bot_on
    msg = data['message']
    if msg == '/start':
        bot_on = True
        qqunilt.send_user_back(data,'机器人已启动')
        return False
    elif msg == '/stop':
        bot_on = False
        qqunilt.send_user_back(data,'机器人已停止')
        return False
    return True

@qqunilt.on_message(message_type='private',sub_type='friend')
def ask(data:dict):
    def callback(user:chater.User,prompt:str,create_time:float,conversation:chater.ChatGPTConversation,*wargs):
        _user = str(user.id).split('-',1)
        if _user[0] == 'user':
            print(f"Handle [user-{_user[1]}]:{prompt}")
            try:
                for i in conversation.split(prompt,'\n\n'):
                    if i == '':continue
                    qqunilt.send_user_back(data,i)
                    # qqunilt.send_user_back(data,mi_maps.handle_res(i,uid=_user[1]))
                    # mi_maps.delete_by_uid(_user[1])
                    print(f"Send [bot->user-{_user[1]}]:" + (i[:40] + '...' if len(i) > 40 else i).replace('\n',' '))
            except chater.error.OnBusy:
                qqunilt.send_user_back(data,'[error]机器人暂时处于繁忙状态,请稍后再次尝试')
                print("[error]机器人暂时繁忙")
            except chater.error.TooManyRequests:
                qqunilt.send_user_back(data,'[error]一小时内过多请求,请稍后再尝试')
                print("[error]请求过多")
            except chater.error.NetWorkException as e:
                qqunilt.send_user_back(data,'[error]网络问题,请再次尝试')
                print("[error]网络问题")
                traceback.print_exception(e)
            except chater.error.GenerateFail as e:
                qqunilt.send_user_back(data,'[error]ChatGPT生成失败,将重置对话')
                try:
                    conversation.delete()
                except Exception as e:
                    print("[error]对话删除失败:" + conversation.uuid)
                    traceback.print_exception(e)
                print("[error]ChatGPT生成错误")
            except chater.error.BaseException as e:
                qqunilt.send_user_back(data,'[error]未知问题,请再次尝试,如果继续发生错误,请联系开发者')
                print("[error]未定义基础错误")
                traceback.print_exception(e)
            except Exception as e:
                qqunilt.send_user_back(data,'[error]程序异常,请联系开发者')
                print("[error]未知错误")
                traceback.print_exception(e)
    try:
        qqunilt.mark_as_read(data)
    except:
        print("标记只读失败")
    if bot_on:
        que.push(chater.GPTAsk(
            chater.User('user-' + str(data['user_id'])),
            'user-' + str(data['user_id']),
            data['message'],
            time.time(),
            callback,
        ))
    return False

que.handle_forever(True)
qqhandler.start_handler()
