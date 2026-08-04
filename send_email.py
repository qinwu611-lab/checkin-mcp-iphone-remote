# -*- coding: utf-8 -*-
"""通过 163 邮箱 SMTP 发送命令邮件到 iPhone

用法：
    python send_email.py "回来" ""
    python send_email.py "睡觉" ""

注意：PASSWORD 填 163 邮箱的【客户端授权码】（不是网页登录密码）。
建议用环境变量读取，不要写死在公开代码里。
"""
import smtplib
import sys
import os
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.163.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
USERNAME = os.environ.get("SMTP_USER", "你的163邮箱@163.com")
PASSWORD = os.environ.get("SMTP_AUTH_CODE", "你的163客户端授权码")  # 不是登录密码！
RECIPIENT = os.environ.get("SMTP_RECIPIENT", USERNAME)


def send(subject: str, content: str = "") -> None:
    msg = EmailMessage()
    msg["From"] = USERNAME
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.set_content(content or "", charset="utf-8")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
    print(f"已发送：主题={subject}，内容={content or '<空>'}")


if __name__ == "__main__":
    subject = sys.argv[1] if len(sys.argv) > 1 else ""
    content = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        send(subject, content)
        print("OK")
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        raise SystemExit(1)
