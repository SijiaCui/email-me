import imaplib
import os
from email import message_from_bytes
from email.header import decode_header

# 163 反垃圾要求 SELECT 前发送 IMAP ID 命令表明客户端身份
imaplib.Commands["ID"] = ('AUTH',)

imap_server = "imap.163.com"  # 服务器硬编码为 163
username = os.getenv("EMAIL_BOT")  # bot 账号,必填(无默认,避免把个人邮箱写进代码)


def _decode(raw):
    """解码可能经过 RFC2047 编码的邮件头。"""
    if raw is None:
        return ""
    parts = []
    for text, enc in decode_header(raw):
        if isinstance(text, bytes):
            parts.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts)


def _body(msg):
    """提取纯文本正文。"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace") if payload else ""
        return ""
    payload = msg.get_payload(decode=True)
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace") if payload else ""


def connect(email_pw=None):
    """建立并返回一个已登录、已 SELECT INBOX 的 IMAP 连接。调用方负责 logout。

    供需要跨多次轮询复用同一连接的场景使用（见 mailbox.wait_for_reply），
    避免每次轮询都重新登录而触发 163 的登录频率限制。
    """
    email_pw = email_pw or os.getenv("EMAIL_PW")
    if not username:
        raise RuntimeError("EMAIL_BOT 未设置(bot 邮箱)")
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    mail.login(username, email_pw)
    # 发送 IMAP ID 命令,满足 163 反垃圾校验
    id_args = ("name", "python-client", "version", "1.0", "vendor", "myclient", "contact", username)
    mail._simple_command("ID", '("' + '" "'.join(id_args) + '")')
    status, _ = mail.select("INBOX")
    if status != "OK":
        raise RuntimeError(f"选择收件箱失败: {status}")
    return mail


def fetch_unread_on(mail):
    """用一个已有连接收取未读邮件。先 NOOP 刷新，让服务器报告期间新到的邮件。"""
    mail.noop()
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        raise RuntimeError(f"搜索邮件失败: {status}")

    results = []
    for num in messages[0].split():
        _, data = mail.fetch(num, "(RFC822)")
        msg = message_from_bytes(data[0][1])
        results.append({
            "num": num.decode("utf-8"),
            "from_addr": _decode(msg.get("From")),
            "subject": _decode(msg.get("Subject")),
            "body": _body(msg),
        })
    return results


def fetch_unread(email_pw=None):
    """一次性收取未读邮件（自建连接并登出），返回 [{num, from_addr, subject, body}]。"""
    mail = connect(email_pw)
    try:
        return fetch_unread_on(mail)
    finally:
        try:
            mail.logout()
        except Exception:
            pass


if __name__ == "__main__":
    for _m in fetch_unread():
        print(f"收到新邮件编号: {_m['num']}")
