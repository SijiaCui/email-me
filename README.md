# email-me

通过**邮件**远程监控、监督并指导 Claude Code。无论你在哪，只要能收发邮件，就能：

- 在**任务停下**、**需要授权/决策**、**重要事件**（训练完成/失败、监控告警）时收到提醒；
- **回复邮件**即可给出下一步指示，Claude 自动据此继续 —— 真正的远程遥控。

## 工作原理

```
Claude 停下 ──Stop hook──▶ 发汇报邮件 ──▶ 阻塞轮询收件箱
                                              │
        你手机回复邮件 ──────────────────────┘
                                              ▼
              {"decision":"block","reason": 你的指示} ──▶ Claude 继续干活 ──▶ 再次停下…
```

回复 `stop` / `结束` 即终止闭环；超时无回复也会自动结束。

## 组成

| 部分 | 触发 | 作用 |
|------|------|------|
| `hooks` Stop | 每次 Claude 停下 | 发汇报邮件并阻塞等你回复，注入指示让 Claude 继续 |
| `hooks` Notification | 需授权/长时间等待输入 | 发提醒邮件（仅提醒，无法远程点"允许"） |
| `skills/notify` | Claude 主动判断重要事件 | 训练/构建完成或失败、监控告警时主动发邮件，可选等待回复 |
| `/email-notify` | 你手动 | 手动发一封提醒，可 `--wait` 等回复 |
| `scripts/monitor.py` | 可选后台进程 | 持续把你的回复落盘到 `inbox/`（非阻塞模式备用） |

## 安装

1. 放进插件目录（或 marketplace），在 Claude Code 里启用 `email-me`。
2. 配置环境变量（在启动 Claude 的 shell 里）：

   ```bash
   export EMAIL_BOT=<bot 发件邮箱(163)，如 your-bot@163.com>
   export EMAIL_PW=<bot 邮箱的 IMAP/SMTP 授权码>
   export EMAIL_PEER=<你的收件邮箱，如 you@example.com>
   export EMAIL_REMOTE=1   # 开启遥控；不设则 Stop/Notification hook 不发邮件
   ```

   > `EMAIL_REMOTE` 是总开关：本地日常使用时不设它，hook 完全静默；要远程盯任务时再 `export EMAIL_REMOTE=1`。

3. bot 账号/对端可用上面的环境变量配置；SMTP/IMAP **服务器硬编码为 163**（`smtp.163.com` / `imap.163.com`），换邮箱服务商需改 `scripts/send.py` / `scripts/receive.py`。

## 配置项

| 变量 | 默认 | 说明 |
|------|------|------|
| `EMAIL_BOT` | 必填 | 发件+被监控的 bot 邮箱（163） |
| `EMAIL_PW` | 必填 | bot 邮箱授权码 |
| `EMAIL_PEER` | 必填 | 你的收件地址 |
| `EMAIL_REMOTE` | 未设 | 设为任意非空值开启 Stop/Notification 邮件遥控 |
| `EMAIL_WAIT_TIMEOUT` | `1500` | Stop hook 等回复的秒数（须 ≤ hooks.json 的 `timeout` 1800） |

## 限制

- Notification（授权请求）只能提醒，无法远程批准 —— 真正的遥控走 Stop 闭环。
- Stop hook 阻塞期间该会话被冻结等待，属预期行为。
- bot 账号可经 `EMAIL_BOT` 配置，但 SMTP/IMAP 服务器硬编码为 163，换服务商需改 `send.py` / `receive.py`。
