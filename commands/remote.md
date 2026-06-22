---
description: Arm/disarm remote control — whether a stop emails you and waits for a reply
argument-hint: on | once | off | status
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/remote.py *)
---

Set the remote-control arm state, then report the result to the user:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/remote.py $ARGUMENTS
```

Modes:
- `on` — stay armed: every stop sends a report email and blocks for the user's
  reply (the remote-control loop), until `off`.
- `once` — arm for the next stop only, then auto-disarm. Good for a single
  decision.
- `off` — disarm (default): stops are silent and end normally.
- `status` / no argument — show the current state.

When not armed (`off`, the default), the Stop/Notification hooks are fully
silent — this is the only master switch.

Arming (`on`/`once`) takes effect from the **next** stop: the arming command is
itself a turn, and the stop that ends it is skipped, so it never sends an email
or consumes a `once`.
