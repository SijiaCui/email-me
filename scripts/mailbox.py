"""收发邮件的公共逻辑：清空旧未读、轮询等待对端回复并落盘。

被 stop_hook.py / notify.py 复用。脚本所在目录已在 sys.path[0]，
因此可直接 import send / receive。
"""
import os
import time
from email.utils import parseaddr

from receive import fetch_unread, connect, fetch_unread_on
from send import PEER, SUBJECT

INBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inbox")

# 终止关键词：回复其中任一即视为结束遥控，不再注入下一步指示
STOP_WORDS = {"stop", "结束", "停止", "退出", "done", "quit"}


def is_from_peer(m):
    """是否来自配置的对端，且不是 bot 自己发出的通知。"""
    if m["subject"].strip() == SUBJECT:
        return False
    return parseaddr(m["from_addr"])[1].lower() == PEER.lower()


def drain(email_pw=None):
    """把当前来自对端的未读邮件标记为已读（轮询前清空历史，避免误读旧回复）。"""
    try:
        for _ in fetch_unread(email_pw):
            pass
    except Exception:
        pass


def persist(m):
    """把一封邮件落盘到 inbox/<num>.txt，返回文件路径。"""
    os.makedirs(INBOX_DIR, exist_ok=True)
    path = os.path.join(INBOX_DIR, f"{m['num']}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"reply_to: {parseaddr(m['from_addr'])[1]}\n")
        f.write(f"subject: {m['subject']}\n")
        f.write("---\n")
        f.write(m["body"])
    return path


def is_stop(body):
    """判断回复是否为终止指令。"""
    return body.strip().lower() in STOP_WORDS


def wait_for_reply(timeout=1500, poll_seconds=15, email_pw=None, log=lambda s: None):
    """阻塞轮询，直到收到对端回复或超时。

    返回 (body, path)；超时返回 (None, None)。
    body 已去掉常见的引用原文部分（按 '----' 或 '原邮件' 截断）。
    """
    email_pw = email_pw or os.getenv("EMAIL_PW")
    deadline = time.time() + timeout
    mail = None  # 跨轮询复用同一连接，避免上百次重复登录触发 163 限流
    try:
        while time.time() < deadline:
            try:
                if mail is None:
                    mail = connect(email_pw)
                for m in fetch_unread_on(mail):
                    if not is_from_peer(m):
                        continue
                    path = persist(m)
                    log(f"收到回复 num={m['num']} -> {path}")
                    return _strip_quote(m["body"]), path
            except Exception as e:
                log(f"轮询出错: {e}")
                mail = _safe_logout(mail)  # 连接可能已坏，下轮重连
            time.sleep(poll_seconds)
        return None, None
    finally:
        _safe_logout(mail)


def _safe_logout(mail):
    if mail is not None:
        try:
            mail.logout()
        except Exception:
            pass
    return None


def _strip_quote(body):
    """截掉客户端自动附带的引用原文，只保留用户实际写的内容。"""
    markers = ("----", "原邮件", "Original Message", "发件人:", "On ")
    cuts = [p for p in (body.find(m) for m in markers) if p > 0]
    if cuts:
        body = body[:min(cuts)]
    return body.strip()
