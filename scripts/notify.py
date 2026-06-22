#!/usr/bin/env python3
"""主动事件提醒 CLI —— 供 Claude 判断"重要事件"时调用，或你手动调用。

用法：
  python3 notify.py "训练任务已完成，准确率 0.93"
  python3 notify.py --wait "构建失败，是否回滚？"   # 阻塞等你回复，回复内容打到 stdout

--wait 时：收到回复 -> 打印到 stdout（Claude 可读取并据此行动）；
          超时/无回复 -> 打印空行，退出码 0。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send import send_email, PEER  # noqa: E402
from mailbox import wait_for_reply, drain, is_stop  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message", help="要提醒的内容")
    ap.add_argument("--wait", action="store_true", help="发送后阻塞等待回复")
    ap.add_argument("--timeout", type=int, default=1500, help="等待回复的秒数")
    args = ap.parse_args()

    if not os.getenv("EMAIL_PW"):
        print("ERROR: EMAIL_PW 未设置", file=sys.stderr)
        sys.exit(1)

    body = f"【重要事件】\n\n{args.message}"
    if args.wait:
        body += "\n\n————————————————\n回复本邮件给出指示。"

    if args.wait:
        drain()
    send_email(body, receiver=PEER)
    print(f"已提醒 {PEER}", file=sys.stderr)

    if not args.wait:
        return

    reply, _ = wait_for_reply(timeout=args.timeout,
                              log=lambda s: print(f"[notify] {s}", file=sys.stderr))
    if reply is None:
        print("")  # 超时
    elif is_stop(reply):
        print("STOP")
    else:
        print(reply)  # 你的指示，交给 Claude


if __name__ == "__main__":
    main()
