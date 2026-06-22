---
description: 拉一次邮箱，把用户主动发来的问题当作查询，查实时状态后回信
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/poll_once.py), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/send.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py *)
---

拉取一次 bot 收件箱，处理用户主动发来的邮件查询。

1. 运行：

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/poll_once.py
   ```

2. 解析 stdout：
   - 输出 `NO_MAIL` → 没有新问题，本次什么都不用做，直接结束。
   - 每个 `===MAIL num=N===` 块后面是用户的一条问题。

3. 对每条问题：把它当作对**当前正在进行的工作**的提问（例如"训练进展如何？""现在第几个 epoch？""有没有报错？"）。
   - 主动收集回答所需的实时状态：`tail` 训练日志、读取 metrics 文件、查看后台任务输出、`git status` 等，**用真实数据回答，不要编造**。
   - 用下面的命令把答案回信给用户（正文用你组织好的简明结论）：

     ```
     python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py "<你的回答>"
     ```

4. 处理完所有邮件后结束本次调用。

> 持续应答：配合 `/loop` 周期运行本命令即可，例如 `/loop 60s /email-watch`，
> 这样用户可以在任意时刻发邮件提问，约一分钟内收到带实时状态的回信。
