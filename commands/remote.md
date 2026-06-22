---
description: 布防/撤防远程遥控——控制 Claude 停下时是否发邮件并等你回复
argument-hint: on | once | off | status
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/remote.py *)
---

运行下面的命令设置远程遥控的布防状态，并把结果告诉用户：

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/remote.py $ARGUMENTS
```

含义：
- `on` —— 持续布防：之后每次你停下都会发汇报邮件并阻塞等用户回复（远程遥控循环），直到 `off`。
- `once` —— 一次性：仅下一次停下时等待，之后自动撤防。适合"就等用户拍一次板"。
- `off` —— 撤防（默认）：停下不打扰，正常结束。
- `status` / 不带参数 —— 查看当前状态。

未布防（off，默认）时 Stop/Notification hook 完全静默——这是唯一的总开关。

布防（`on`/`once`）从**下一次** Claude 停下才生效：布防命令本身是一个回合，其回合结束的停下会被自动跳过，不会触发邮件、也不会消费 `once`。
