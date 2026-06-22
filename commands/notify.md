---
description: Email an alert to the configured address (optionally block for a reply)
argument-hint: [--wait] <message>
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py *)
---

Send an alert to the user's email. If the arguments include `--wait`, the
command blocks until the user replies and prints the reply to stdout — read it
and act on the user's instruction.

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py $ARGUMENTS
```
