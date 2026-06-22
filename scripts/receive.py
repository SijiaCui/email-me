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


def _connect(email_pw):
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


def fetch_unread(email_pw=None):
    """收取未读邮件，返回 [{num, from_addr, subject, body}] 列表。"""
    email_pw = email_pw or os.getenv("EMAIL_PW")
    mail = _connect(email_pw)
    try:
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
    finally:
        mail.logout()


def receive_emails(email_pw=None):
    """收取未读邮件并打印编号，返回编号列表。"""
    nums = []
    for m in fetch_unread(email_pw):
        nums.append(m["num"])
        print(f"收到新邮件编号: {m['num']}")
    return nums


if __name__ == "__main__":
    receive_emails()
