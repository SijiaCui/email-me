import os
import sys
import time
from email.utils import parseaddr

from receive import fetch_unread
from send import PEER

POLL_SECONDS = 15
REPLY_SUBJECT = "CC-Notice"  # 跳过自己发出的回复,避免死循环
INBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inbox")


def monitor():
    """持续轮询未读邮件。每封新请求写入 inbox/<num>.txt 并打印一行事件。"""
    os.makedirs(INBOX_DIR, exist_ok=True)
    email_pw = os.getenv("EMAIL_PW")
    if not email_pw:
        print("ERROR: EMAIL_PW 未设置", flush=True)
        sys.exit(1)

    while True:
        try:
            for m in fetch_unread(email_pw):
                if m["subject"].strip() == REPLY_SUBJECT:
                    continue  # 自己的回复,忽略
                reply_to = parseaddr(m["from_addr"])[1]
                if reply_to.lower() != PEER.lower():
                    continue  # 只处理来自配置对端的邮件
                path = os.path.join(INBOX_DIR, f"{m['num']}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"reply_to: {reply_to}\n")
                    f.write(f"subject: {m['subject']}\n")
                    f.write("---\n")
                    f.write(m["body"])
                # Monitor 工具按行捕获:这一行就是一个事件
                print(f"NEW_MAIL num={m['num']} from={reply_to} file={path}", flush=True)
        except Exception as e:
            print(f"POLL_ERROR: {e}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    monitor()
