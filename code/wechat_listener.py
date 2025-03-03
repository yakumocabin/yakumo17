import itchat
from itchat.content import TEXT
import datetime

# 设置要监听的用户昵称
TARGET_USER = '目标用户昵称'

# 登录微信
itchat.auto_login(hotReload=True)

# 消息处理函数
@itchat.msg_register(TEXT)
def text_reply(msg):
    # 检查消息是否来自目标用户
    if msg['User']['NickName'] == TARGET_USER:
        print(f"收到来自 {TARGET_USER} 的消息：{msg['Text']}")
        # 将消息存储到文件
        with open(f"{TARGET_USER}_messages.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {msg['Text']}\n")

# 保持微信在线
itchat.run()
