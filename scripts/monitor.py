import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from receive import fetch_unread  # noqa: E402
from mailbox import is_from_peer, persist  # noqa: E402

POLL_SECONDS = 15


def monitor():
    """持续轮询未读邮件。每封来自对端的新邮件落盘到 inbox/ 并打印一行事件。

    非阻塞模式的备用入口；阻塞遥控走 stop_hook.py。复用 mailbox 的过滤/落盘逻辑。
    """
    email_pw = os.getenv("EMAIL_PW")
    if not email_pw:
        print("ERROR: EMAIL_PW 未设置", flush=True)
        sys.exit(1)

    while True:
        try:
            for m in fetch_unread(email_pw):
                if not is_from_peer(m):
                    continue
                path = persist(m)
                # Monitor 工具按行捕获:这一行就是一个事件
                print(f"NEW_MAIL num={m['num']} file={path}", flush=True)
        except Exception as e:
            print(f"POLL_ERROR: {e}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    monitor()
