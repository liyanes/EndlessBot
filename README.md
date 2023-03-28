# Endless Bot

一个机器人,基于ChatGPT与Go-CQHTTP

## 安装

```bash
pip install -r requirements.txt
git clone https://github.com/liyanes/EndlessBot.git
```

## 配置

```bash
cd src
touch .env
echo API_KEY=(你的API密匙)>.env
echo PROXY=(代理端口)>.env
echo LOG_LEVEL=WARNING>.env
echo CONSOLE_LOG_LEVEL=INFO>.env
echo ENABLE_LOG=1>.env
```

## 使用

> 请先配置好Go-CQHTTP

选择HTTP上报模式
端口5701事件上报
端口5700侦听

然后

```bash
python3 qqbot_api.py
```

## 功能

指令暂时没有文档

可以在私聊或群聊中利用ChatGPT端口回答问题
