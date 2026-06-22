# email-me

**English** · [中文](README-CN.md)

Monitor, supervise, and steer Claude Code remotely **over email**. Wherever you
are, as long as you can send and receive mail, you can:

- get notified when a **task stops**, when Claude **needs permission/a decision**,
  or on **important events** (training finished/failed, monitoring alerts);
- **reply to the email** with your next instruction and Claude continues
  automatically — genuine remote control.

## How it works

```
/email-me:remote on ──arm──▶ Claude stops ──Stop hook──▶ send report email ──▶ poll inbox (blocking)
                                                              │
              you reply from your phone ─────────────────────┘
                                                              ▼
              {"decision":"block","reason": your instruction} ──▶ Claude keeps working ──▶ stops again…
```

Before you step away, `/email-me:remote on` to arm (or `once` to wait just one
time). Back at the keyboard, or reply `stop` / `结束`, to disarm and end the
loop; a wait with no reply also times out. **When not armed (the default),
every stop is silent and undisturbed.**

## Components

| Part | Trigger | Role |
|------|---------|------|
| `hooks` Stop | every time Claude stops **and armed** | sends a report email and blocks waiting for your reply, injecting it so Claude continues |
| `hooks` Notification | Claude needs permission / long idle **and armed** | sends an alert email (alert only — can't remotely click "allow") |
| `/email-me:remote` | you, manually | arm/disarm: `on`/`once`/`off`, controls whether a stop emails and waits |
| `skills/notify` | Claude judges an event important | proactively emails on training/build done-or-failed, monitoring alerts; can optionally wait for a reply |
| `/email-me:notify` | you, manually | send one alert by hand; `--wait` to block for a reply |
| `/email-me:watch` | you ask, unprompted | poll the inbox once, treat your mail as a query, gather live state and reply; pair with `/loop` to keep it running |
| `scripts/monitor.py` | optional background process | continuously persists your replies to `inbox/` (fallback for non-blocking mode) |

> Commands carry the plugin namespace prefix `email-me:`; typing a bare `/watch`
> may report `Unknown command` when ambiguous.

## User-initiated queries (check task progress)

The opposite of "event → notification": with no event triggering it, you email
a question **at any time**, e.g. "How's the training going?". The key point is
that answering this needs Claude to look at live state, so inbound queries work
by **having Claude poll the inbox periodically and reply**:

```
# run the long task in the background, then keep Claude answering (~once a minute)
/loop 60s /email-me:watch
```

Each tick: `scripts/poll_once.py` does one non-blocking fetch → any mail from you
is handed to Claude → Claude `tail`s logs / reads metrics and answers from real
data → `scripts/notify.py` mails the answer back. If there's no new mail the
tick is a no-op.

> Zero-config alternative: run training in the background, let Claude sit at a
> Stop, and `stop_hook`'s blocking wait is itself a Q&A window — your question is
> injected and Claude's answer becomes the next report email. Good for a one-off
> follow-up; for "ask repeatedly, don't end on timeout" use the
> `/loop 60s /email-me:watch` above.

## Install

> Requires a Claude Code with plugin support (the `claude plugin` command). This
> repo ships `.claude-plugin/marketplace.json`, so it can be added as a
> marketplace directly.

### 1. Install the plugin

**Project-scoped** (enabled only in the current project, good for watching one
task temporarily):

```bash
claude plugin marketplace add SijiaCui/email-me --scope project
claude plugin install email-me@ohocui-plugins --scope project
```

**Global** (available in all projects): drop `--scope project` (defaults to user
scope).

> A local path also works instead of the GitHub repo:
> `claude plugin marketplace add ./email-me --scope project` (after `git clone`).

After installing, **restart Claude Code** (or `/reload-plugins`) so the commands,
hooks, and skill take effect; run `claude plugin list` and confirm
`email-me@ohocui-plugins` is enabled.

### 2. Configure environment variables

In the **shell that launches Claude**:

```bash
export EMAIL_BOT=<bot sender mailbox (163), e.g. your-bot@163.com>
export EMAIL_PW=<the bot mailbox's IMAP/SMTP auth code>
export EMAIL_PEER=<your receiving mailbox, e.g. you@example.com>
```

> **Arm switch**: the Stop/Notification hooks default to `off` and are fully
> silent — they won't disturb you on every stop. To watch a task remotely, arm
> with `/email-me:remote on` (or `once` to wait just one time) and the hooks
> will email + wait; `off` disarms. This is the single master switch — no
> environment variable needed to enable it.
> The SMTP/IMAP **servers are hardcoded to 163** (`smtp.163.com` /
> `imap.163.com`); switching providers means editing `scripts/send.py` /
> `scripts/receive.py`.

### 3. Verify

```bash
/email-me:notify just testing         # you should receive an alert email
```

> The first time a script sends mail, Claude Code prompts for permission — pick
> "allow". In automated modes it may be blocked; confirm manually, or add rules
> to `permissions.allow` in `.claude/settings.local.json`:
> ```json
> "Bash(python3 *)", "Skill(email-me:notify)"
> ```

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `EMAIL_BOT` | required | the bot mailbox that sends and is monitored (163) |
| `EMAIL_PW` | required | the bot mailbox's auth code |
| `EMAIL_PEER` | required | your receiving address |
| `EMAIL_WAIT_TIMEOUT` | `1500` | seconds the Stop hook waits for a reply (must be ≤ `hooks.json`'s `timeout` of 1800) |

## Limitations

- Notification (permission requests) can only alert, not approve remotely — real
  remote control goes through the Stop loop.
- While the Stop hook blocks, that session is frozen waiting; this is expected.
- The bot account is configurable via `EMAIL_BOT`, but the SMTP/IMAP servers are
  hardcoded to 163; switching providers means editing `send.py` / `receive.py`.
