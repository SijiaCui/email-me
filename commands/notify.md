---
description: 给配置的邮箱发一封提醒邮件（可选阻塞等待回复）
argument-hint: [--wait] <提醒内容>
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py *)
---

运行下面的命令把提醒发到用户邮箱。若用户参数里含 `--wait`，命令会阻塞等待回复，
回复内容会打到 stdout —— 读取它并据此执行用户的下一步指示。

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py $ARGUMENTS
```
