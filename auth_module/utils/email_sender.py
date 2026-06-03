from datetime import datetime
from typing import Optional


class EmailSender:
    def send(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError


class ConsoleEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str) -> bool:
        print("=" * 60)
        print(f"EMAIL SENT (DEV MODE)")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("-" * 60)
        print(body)
        print("=" * 60)
        return True


class SMTPEmailSender(EmailSender):
    def __init__(self, host: str, port: int, username: str, password: str, use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, to: str, subject: str, body: str) -> bool:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        try:
            server = smtplib.SMTP(self.host, self.port)

            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            server.quit()

            return True
        except Exception:
            return False


def get_email_sender() -> EmailSender:
    mode = "console"

    if mode == "console":
        return ConsoleEmailSender()

    return ConsoleEmailSender()