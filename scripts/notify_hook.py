#!/usr/bin/env python3
"""Notification hook —— Claude 需要授权或长时间等待输入时，发邮件提醒你。

Notification 事件不支持注入决策（无法远程点"允许"），因此这里只做提醒：
告诉你 Claude 卡在哪了，你可以回电脑处理，或在随后的 Stop 闭环里遥控。

仅在已布防（/email-me:remote on|once）时启用，默认 off 完全静默。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send import send_email, PEER  # noqa: E402
from mailbox import arm_state, is_fresh  # noqa: E402


def main():
    if arm_state() == "off":
        sys.exit(0)  # 未布防（默认）：不打扰
    if is_fresh():
        sys.exit(0)  # 刚布防，本回合不打扰（fresh 由 stop hook 吸收清除）
    if not os.getenv("EMAIL_PW"):
        sys.exit(0)
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    msg = payload.get("message", "Claude 需要你的关注")
    body = (
        "【Claude 需要你的关注 / 授权】\n\n"
        f"{msg}\n\n"
        "————————————————\n"
        "请回到电脑处理，或等它停下后通过邮件遥控。"
    )
    try:
        send_email(body, receiver=PEER)
    except Exception as e:
        print(f"[notify_hook] 发送失败: {e}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
