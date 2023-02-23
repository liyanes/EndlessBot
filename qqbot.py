import qqunilt
import qqhandler
import time
import chater

bot = chater.ChatGPTBot({
    'auth':{
        'session_token':'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0.._VkZjdhHhMjkPhnD.J6xrv4-3Yi0ONtgzc0p8_CdUhWrxYMON4cc5FgNpWnhJwgwHSeoIGktd7_BypqN1Sj1ufrNXm1VdnMcKiZOlx1gCoCXQNIBKsjCkhrDwdbRd1Hsqy2DXDxZwDnOYpGVqvPx2wwSn8lYaYwdk-wfDFQpq3rAnwiTEzeoI0LgHhJ2GZfx6qxLeXxj7dqlLLtDLK9EOthCQ8rIV7g7UcbkVOe25DxJRyrQlYNAMZ_Er0SfI9r-VLjlAnB9A8vWJG2NOxZtwvvSeKviJLIZ1qM7aY94KNbmmtnbP5nDyCtnZWrcGZU_51KUgHd2omr6J-AvuTCAaLaQg8fnIMOHacK0RvXr080-iLMDWb6qHPeK3xtCw29qOi8c_Np2MS6a8nWF5QxJIJmwX3ozS2fiZ70BgDLAncYMuDMMJfZ8wTMLTfYtFdxHb8RM8n80ZYteMXeCUatEJIk0NOwjjtOQGDBXN-OBB4bkvl5Ec05d3SMTwVUpCnzLUyWvb9fTbFZnZCgZ1fwFv_Fj7ge8p3aUh7oIOQHgInJyF1njNhCxulFAuAuA-Qx2Hkj62rvv9KtRInRuiSBAYZbkrF9fc6GhgsLhA0Pc9OlKOMcBZi3XR5w3ii8lW1DvEwLkhecGh2mp_495lR-Ah-JGLJLHO45awmR-DUAfmtZpy-9arRNmK0zVzF2_KUhC1INclAWAPJPJDeuEkmNzILRTZj-6JAuXoa-XJw6BVA-Nv3-ZcJuwg8VHj8nBOsz-C3qXvTbucmDxWQZ8dWKwu0kSL2bt-GPdEEwY-f3l0vLxCd4JvKvng5wkerhvcXK18mQcBlckInVRQMsT3QIuFHLieKfIjequQzAZjpD1_uUkErWnKJE0lA50Uniqwm_mVbTiGKvi8TzYaK6UfwhTYv4Ku-rLOT7Hd0vOkN-hw69-U2BYo4aQFWAMaJdU_RzhRXsZvGO_YBXkEJyMYNOv4nTVPEEEhGgfgDaOAR9bJj1Hz7y5gjFQGn0y-efnyWbXIn2VLcXJsx7wUILrI03LsJpabMdF6u8N4rKr9L40qYcmdFcpUQ_DYJ3AhK1T4gRaa-jDrIVJSmpnZkzP8XpeJIfj5UEpQpA6u77uPpwIFB-9_nqZDXw5VdKLbR5cjNv9Lk2p2dG9qfHcrqhSQWQapnCzx_f1yy5ECCa7yo2gHqqdc15qz0DVo9B3n__RWNO9-tbdbE74SMx11NicU3l-_HK64m8Evb1ui-2NJ3ZwDZK_cptI-uJb528BJ3lAaktn3Lbv2g8CPwUbxgknvySixAFyW_h5qJCMdisWhyi-GU2Y5eagWbBNOcSicTo4O_pI9r2JyX7pLMsJSi4_A_ByjmSpO2umTW-EbJJUSucDf6j_reII3VUpH7h1t_HA6YA7xrJZnc_ZK7XVCgGeHBkUmjyWnQwxG47KAeBn_X-tvANsr-TSkU6b21nrqX-SgmlKrThUfCCHhI9S5lcd2eD_-jZ9CpzSaRx1hsapcXfTMH0tY9OpZL0SAQjNZXcdvj9OZb39qLuq5p6iR8F7MwyQ16M2TD3qVGCDfxwkzXaWkN6Z7_jMmJj2FMuoM9BAizbcvM9fHpgRFEysvfwG49Q6DeJDXy_P3ES2nwy22Jk29PuSeg33FDUfRG7mPHBR0tf4Kf69wpI3hM19GZCRRz7q8a7xrhJKJbDsdWPdWRZTx8Yf5XTrP7HM4F3T511baQXIEfhIaFpZAE8C-Codnr4Rch1ZbWio7k9IDUFNXfM_C0if7YsSOL9EoZGYlKsuwWT8ChYfhrq7PHbm23otTeuj_6cGQilZ9waUKs-6cs9K8aHNikUBUum5q6XRhD4gwqlP748uIW97TFjL-jdhew1MyjZzJQs-i6-pMfLEDYzz5eCZDPRIfr9KmAkwnY3hsJkzEw6vivtuRdlJFfmYwhKjBc66gA7qjH3dZ1UDrj9XSKlp9Cvy0baTGe7-DBkgXkIqlcDNzvZ3wRI1HmBpyt8cwfiTvDPz0gnh8fPotzMr0HaQgO7es9Ww5dRrKTw2-bNC_N8viVA6c_tBRitUlPlGU1nF0GlNtHbgOwSQQfczPZ5wlynvq_BSyRb0utl_K8kxDw41moUvPO_EMwvW8Y8oIAqUWzagkR1bY4Y0Ay3EZ2bJcL7xmvhY71G2wRWSAlbi4-zM2DtVrxZhakR1nlWzk8FB2owI_2Nh3plI4YJ6nSowlEfkd9f0NTriRRb-uN17vT4ey4dwOhnkYSTfAE60ki3nmrtR5rg-qntBdx42zNeUBzRU8zhI40yJImuUADN0OMUeL07jaarJK9HVkMkQKr7DnHe6sUwhsZfQ_3JC5WARXhH6Q99YK0AchBGhFSXBVa3ssBFHBb9yswn1b_WARkgmzflq3AExSSvjkWiL8AT7eel8xD3G3SwlzXPSVH8uIjydxNuBijXGF4THHoLZ30bJSwU4zyb4gh0Z23UwOLA1V9h-fxSz1rlJb9m-uRcs0so3ojFiUX6v8WzbwqgmzG4cJVfM1VDguCYLZRwm5kLJYjo4cj0UpcXukB81ql5eH4bPemNZTtgyTt9VQCiaUnyH6xx-MmAACwTtAcXt0ESNzFCkCktqltYVoeHD0TjAHDMd-rPywCsoyTZWFPrWvsQd4Aktgu2X24ttm1A4bd9ITcek.gH2vUPHWDs4dXWAHgP7oVQ'
    },
    'proxy':'http://localhost:10809'
})

que = chater.ChatGPTAskQueue(bot)

print("机器人初始化完成")

@qqunilt.on_message(message_type='private',sub_type='friend')
def ask(data:dict):
    def callback(user:chater.User,prompt:str,create_time:float,conversation:chater.ChatGPTConversation,*wargs):
        _user = str(user.id).split('-',1)
        if _user[0] == 'user':
            try:
                for i in conversation.split(prompt,'\n\n'):
                    qqunilt.send_user_back(data,i)
            except chater.error.OnBusy:
                qqunilt.send_user_back(data,'[error]机器人暂时处于繁忙状态,请稍后再次尝试')
            except chater.error.TooManyRequests:
                qqunilt.send_user_back(data,'[error]一小时内过多请求,请稍后再尝试')
            except chater.error.NetWorkException:
                qqunilt.send_user_back(data,'[error]网络问题,请再次尝试')
            except chater.error.BaseException:
                qqunilt.send_user_back(data,'[error]未知问题,请再次尝试,如果继续发生错误,请联系开发者')
            except Exception:
                qqunilt.send_user_back(data,'[error]程序异常,请联系开发者')
            
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
