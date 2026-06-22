# email-me

[English](README.md) · **中文**

通过**邮件**远程监控、监督并指导 Claude Code。无论你在哪，只要能收发邮件，就能：

- 在**任务停下**、**需要授权/决策**、**重要事件**（训练完成/失败、监控告警）时收到提醒；
- **回复邮件**即可给出下一步指示，Claude 自动据此继续 —— 真正的远程遥控。

## 工作原理

```
/email-me:remote on ──布防──▶ Claude 停下 ──Stop hook──▶ 发汇报邮件 ──▶ 阻塞轮询收件箱
                                                              │
            你手机回复邮件 ──────────────────────────────────┘
                                                              ▼
              {"decision":"block","reason": 你的指示} ──▶ Claude 继续干活 ──▶ 再次停下…
```

走开前 `/email-me:remote on` 布防（或 `once` 只等一次）；回到电脑或回复 `stop`/`结束` 即撤防、终止闭环；超时无回复也会自动结束。**未布防时（默认）每次停下都不打扰**。布防从**下一次**停下才生效——布防命令所在回合自身的停下会被跳过，不会触发邮件、也不会浪费 `once`。

## 组成

| 部分 | 触发 | 作用 |
|------|------|------|
| `hooks` Stop | 每次 Claude 停下**且已布防** | 发汇报邮件并阻塞等你回复，注入指示让 Claude 继续 |
| `hooks` Notification | 需授权/长时间等待输入**且已布防** | 发提醒邮件（仅提醒，无法远程点"允许"） |
| `/email-me:remote` | 你手动 | 布防/撤防：`on`/`once`/`off`，控制停下时是否发邮件等待 |
| `skills/notify` | Claude 主动判断重要事件 | 训练/构建完成或失败、监控告警时主动发邮件，可选等待回复 |
| `/email-me:notify` | 你手动 | 手动发一封提醒，可 `--wait` 等回复 |
| `/email-me:watch` | 你主动发问 | 拉一次邮箱，把你发来的问题当查询，查实时状态后回信；配 `/loop` 常驻 |
| `scripts/monitor.py` | 可选后台进程 | 持续把你的回复落盘到 `inbox/`（非阻塞模式备用） |

> 命令带插件命名空间前缀 `email-me:`，直接敲 `/watch` 在有歧义时会报 `Unknown command`。

## 用户主动发问（查询任务进展）

和上面的「事件 → 通知」相反：没有事件触发，你在**任意时刻**主动发邮件问，例如
"训练进展如何？"。要点是——回答这种问题需要 Claude 看实时状态，所以入站查询靠
**让 Claude 周期性拉邮箱并回信**实现：

```
# 长任务放后台跑，然后让 Claude 常驻应答（约每分钟应答一次）
/loop 60s /email-me:watch
```

每个 tick：`scripts/poll_once.py` 非阻塞拉一次未读 → 有你发来的邮件就交给 Claude →
Claude `tail` 日志 / 读 metrics，用真实数据组织回答 → `scripts/notify.py` 回信给你。
无新邮件则该 tick 空过。

> 零配置替代：训练放后台、让 Claude 停在 Stop，`stop_hook` 的阻塞等待本身就是
> 一个问答窗口——你发问会被注入，Claude 的回答即下一封汇报邮件。适合一次性追问；
> 要"随时反复问、不因超时结束"，用上面的 `/loop 60s /email-me:watch`。

## 安装

> 需要带插件功能的 Claude Code（`claude plugin` 命令）。本仓库已含 `.claude-plugin/marketplace.json`，可直接作为 marketplace 添加。

### 1. 安装插件

**项目级**（只在当前项目启用，适合临时盯某个任务）：

```bash
claude plugin marketplace add SijiaCui/email-me --scope project
claude plugin install email-me@ohocui-plugins --scope project
```

**全局**（所有项目可用）：去掉 `--scope project` 即可（默认 user 级）。

> 也可用本地路径代替 GitHub repo：`claude plugin marketplace add ./email-me --scope project`（先 `git clone` 到本地）。

装完**重启 Claude Code**（或 `/reload-plugins`）让命令、hooks、skill 生效；用 `claude plugin list` 确认 `email-me@ohocui-plugins` 为 enabled。

### 2. 配置环境变量

在**启动 Claude 的 shell** 里：

```bash
export EMAIL_BOT=<bot 发件邮箱(163)，如 your-bot@163.com>
export EMAIL_PW=<bot 邮箱的 IMAP/SMTP 授权码>
export EMAIL_PEER=<你的收件邮箱，如 you@example.com>
```

> **布防开关**：Stop/Notification hook 默认 `off`、完全静默，不会被每次停下打扰。要远程盯任务时用 `/email-me:remote on`（或 `once` 只等一次）布防，hook 才会发邮件+等待；`off` 撤防。这是唯一的总开关，无需任何环境变量。
> SMTP/IMAP **服务器硬编码为 163**（`smtp.163.com` / `imap.163.com`），换服务商需改 `scripts/send.py` / `scripts/receive.py`。

### 3. 验证

```bash
/email-me:notify 测试一下         # 应收到一封提醒邮件
```

> 首次运行脚本发信时，Claude Code 会弹权限请求，选「允许」即可；自动模式下可能被拦，手动确认或在 `.claude/settings.local.json` 的 `permissions.allow` 里加规则放行：
> ```json
> "Bash(python3 *)", "Skill(email-me:notify)"
> ```

## 配置项

| 变量 | 默认 | 说明 |
|------|------|------|
| `EMAIL_BOT` | 必填 | 发件+被监控的 bot 邮箱（163） |
| `EMAIL_PW` | 必填 | bot 邮箱授权码 |
| `EMAIL_PEER` | 必填 | 你的收件地址 |
| `EMAIL_WAIT_TIMEOUT` | `1500` | Stop hook 等回复的秒数（须 ≤ hooks.json 的 `timeout` 1800） |

## 限制

- Notification（授权请求）只能提醒，无法远程批准 —— 真正的遥控走 Stop 闭环。
- Stop hook 阻塞期间该会话被冻结等待，属预期行为。
- bot 账号可经 `EMAIL_BOT` 配置，但 SMTP/IMAP 服务器硬编码为 163，换服务商需改 `send.py` / `receive.py`。
