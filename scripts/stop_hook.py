#!/usr/bin/env python3
"""Stop hook —— 远程遥控闭环的核心。

每当 Claude 停下来，本脚本：
  1. 从 transcript 里取出 Claude 最后说的话，作为汇报；
  2. 发一封邮件给你（手机随时可看）；
  3. 原地阻塞轮询收件箱，等你回复；
  4. 收到回复 -> 输出 {"decision":"block","reason": 你的指示}，Claude 自动据此继续；
     回复 stop/结束 -> 放行，会话真正结束；
     超时无回复 -> 放行。

仅在环境变量 EMAIL_REMOTE 为真时启用，避免本地日常使用被打扰。
需要 EMAIL_PW（bot 邮箱授权码），可选 EMAIL_PEER（你的收件地址）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send import send_email, PEER  # noqa: E402
from mailbox import wait_for_reply, drain, is_stop, arm_state, disarm  # noqa: E402

# hook 整体最长等待（秒）。须 <= hooks.json 里配置的 timeout。
WAIT_TIMEOUT = int(os.getenv("EMAIL_WAIT_TIMEOUT", "1500"))


def _log(s):
    print(f"[stop_hook] {s}", file=sys.stderr, flush=True)


def _last_assistant_text(transcript_path):
    """从 JSONL transcript 中提取 Claude 最后一条文本消息。"""
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    last = ""
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") != "assistant":
                    continue
                content = ev.get("message", {}).get("content", [])
                if isinstance(content, str):
                    last = content
                elif isinstance(content, list):
                    texts = [b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text"]
                    if any(texts):
                        last = "\n".join(t for t in texts if t)
    except Exception as e:
        _log(f"解析 transcript 失败: {e}")
    return last.strip()


def main():
    if not os.getenv("EMAIL_REMOTE"):
        sys.exit(0)  # 功能总闸未开，正常放行
    mode = arm_state()
    if mode == "off":
        sys.exit(0)  # 未布防：停下不打扰（默认），不发邮件、不阻塞
    if not os.getenv("EMAIL_PW"):
        _log("EMAIL_PW 未设置，跳过")
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # stop_hook_active 为真表示本次继续正是由上一轮 block 触发的；
    # 这正是遥控循环的预期形态，无需在此打断（由人是否回复 + 超时自然收敛）。
    summary = _last_assistant_text(payload.get("transcript_path", ""))
    if not summary:
        summary = "（本轮无文本输出）"

    body = (
        "【Claude 任务已停下，等待你的下一步指示】\n\n"
        f"Claude 刚才：\n{summary[:3000]}\n\n"
        "————————————————\n"
        "直接回复本邮件给出下一步指示，Claude 会自动继续。\n"
        f"回复 stop / 结束 可终止会话。{WAIT_TIMEOUT // 60} 分钟无回复则结束。"
    )

    drain()  # 清掉历史未读，避免把旧邮件当成本轮回复
    try:
        send_email(body, receiver=PEER)
        _log(f"汇报邮件已发往 {PEER}，开始等待回复…")
    except Exception as e:
        _log(f"发送失败，放行: {e}")
        sys.exit(0)

    if mode == "once":
        disarm()  # 邮件已发出才消费一次性布防；发送失败则不消费，下次停下重试

    reply, _ = wait_for_reply(timeout=WAIT_TIMEOUT, email_pw=os.getenv("EMAIL_PW"), log=_log)
    if reply is None:
        _log("超时无回复，放行")
        sys.exit(0)
    if is_stop(reply):
        disarm()  # 用户喊停，撤防，避免后续每次停下又重新等待
        _log("收到终止指令，撤防并放行")
        sys.exit(0)

    # 把你的邮件指示注入回 Claude，让它继续
    print(json.dumps({
        "decision": "block",
        "reason": f"用户通过邮件发来下一步指示，请据此继续：\n\n{reply}",
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
