#!/usr/bin/env python3
"""非阻塞拉取一次 bot 收件箱，把来自用户的新邮件（问题）打印到 stdout。

供"用户主动发问"应答器使用：每个 tick 调用一次，Claude 读取 stdout 决定是否回信。
输出格式：每封邮件一个块，便于 Claude 解析；无新邮件则只打印 NO_MAIL。

  ===MAIL num=13===
  训练进展如何？

退出码恒为 0（无邮件也算正常）。需要 EMAIL_BOT / EMAIL_PW / EMAIL_PEER。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mailbox import poll_pending  # noqa: E402


def main():
    if not os.getenv("EMAIL_PW"):
        print("ERROR: EMAIL_PW 未设置", file=sys.stderr)
        sys.exit(1)
    try:
        msgs = poll_pending()
    except Exception as e:
        print(f"POLL_ERROR: {e}", file=sys.stderr)
        sys.exit(0)
    if not msgs:
        print("NO_MAIL")
        return
    for m in msgs:
        print(f"===MAIL num={m['num']}===")
        print(m["body"])


if __name__ == "__main__":
    main()
