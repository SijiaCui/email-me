---
description: Fetch the inbox once; answer any user email with live task state
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/poll_once.py), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/send.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py *)
---

Poll the bot inbox once and answer any questions the user emailed.

1. Run:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/poll_once.py
   ```

2. Parse stdout:
   - `NO_MAIL` → no new questions; do nothing and finish.
   - Each `===MAIL num=N===` block is followed by one question from the user.

3. For each question, treat it as being about the **work currently in progress**
   (e.g. "How's training going?", "Which epoch now?", "Any errors?").
   - Gather the live state needed to answer: `tail` the training log, read the
     metrics file, check background task output, `git status`, etc. **Answer
     from real data — never make it up.**
   - Email the answer back (body = your concise conclusion):

     ```
     python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notify.py "<your answer>"
     ```

4. Finish once all emails are handled.

> Standing responder: run this on an interval with `/loop`, e.g.
> `/loop 60s /email-me:watch`, so the user can ask anytime and get a reply with
> live state within about a minute.
