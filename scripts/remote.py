#!/usr/bin/env python3
"""布防开关：控制 Stop/Notification hook 停下时是否发邮件并等待回复。

  remote.py on       持续布防：每次停下都发邮件、等你回复（远程遥控循环）
  remote.py once     一次性：仅下一次停下等待，之后自动撤防
  remote.py off      撤防：停下不打扰（默认）
  remote.py status   查看当前状态（默认）

布防状态存在文件里，可在会话运行中随时切换，无需重启 shell。
注意：还需 EMAIL_REMOTE=1（功能总闸）布防才会真正生效。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mailbox import arm_state, set_arm  # noqa: E402

_DESC = {"on": "持续布防：每次停下都发邮件等回复",
         "once": "一次性布防：仅下一次停下等待",
         "off": "已撤防：停下不打扰"}


def main():
    arg = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    if arg == "status":
        cur = arm_state()
        print(f"remote = {cur}（{_DESC[cur]}）")
    else:
        try:
            set_arm(arg)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        print(f"remote -> {arg}（{_DESC[arg]}）")

    if not os.getenv("EMAIL_REMOTE"):
        print("提示：EMAIL_REMOTE 未设置，hook 不会生效；请先 export EMAIL_REMOTE=1。",
              file=sys.stderr)


if __name__ == "__main__":
    main()
