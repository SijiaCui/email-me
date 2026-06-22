import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import os
import sys

smtp_server = "smtp.163.com"  # 服务器硬编码为 163
sender = os.getenv("EMAIL_BOT")  # bot 账号,必填(无默认,避免把个人邮箱写进代码)
PEER = os.getenv("EMAIL_PEER")  # 对端(你的)收件地址,必填

SENDER_NAME = "CC-bot"
SUBJECT = "CC-Notice"


def send_email(body, receiver=None, email_pw=None):
    """发送一封邮件。发件人昵称固定为 CC-bot，主题固定为 CC-Notice。
    receiver 默认为 PEER(可用 EMAIL_PEER 配置)。"""
    receiver = receiver or PEER
    email_pw = email_pw or os.getenv("EMAIL_PW")
    if not sender:
        raise RuntimeError("EMAIL_BOT 未设置(bot 发件邮箱)")
    if not receiver:
        raise RuntimeError("EMAIL_PEER 未设置(你的收件邮箱)")

    message = MIMEText(body, "plain", "utf-8")
    message["From"] = formataddr((SENDER_NAME, sender))
    message["To"] = formataddr((str(Header("收件人", "utf-8")), receiver))
    message["Subject"] = Header(SUBJECT, "utf-8")

    server = None
    try:
        # 163 SSL 端口通常为 465
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(sender, email_pw)
        server.sendmail(sender, [receiver], message.as_string())
        # 走 stderr：stdout 是 hook 决策 JSON / notify --wait 指令的专用通道，不能污染
        print("邮件发送成功", file=sys.stderr)
    finally:
        if server is not None:
            server.quit()


if __name__ == "__main__":
    send_email("你好")
