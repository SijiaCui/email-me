---
name: notify
description: Email the user when an important event needs their attention — a long-running task (training, build, deploy) finished or failed; a check or monitor found an anomaly or alert; or a decision is needed before continuing. Use when the event matters and the user may be away from the keyboard.
---

# Notify the user by email

Proactively reach the user by email on important events so they can stay aware
and steer the task from anywhere.

## When to use
- A long-running task (training / build / deploy) **finished or failed**.
- Monitoring, a scan, or tests found an **anomaly or alert**.
- You hit a fork that **needs the user's decision** to continue.

Do not use this for routine or trivial pauses.

## How to use

Notify only (returns immediately, no wait):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py "Training done: 5 epochs, val_acc=0.93"
```

When you need the user to decide, add `--wait` to block for a reply, which is
printed to stdout:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py --wait "Build failed — roll back to the previous version?"
```

Read the command's stdout as the user's instruction:
- plain text → proceed per its content;
- `STOP` → the user asked to stop; do not continue;
- empty → timed out with no reply; decide whether to keep waiting or take a safe default.

## Requirements
Needs `EMAIL_PW` (the bot mailbox auth code); the recipient defaults to `EMAIL_PEER`.
