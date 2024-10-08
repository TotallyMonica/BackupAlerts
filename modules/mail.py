import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket


class Mail:
    def __init__(self, recipients, sender: str, username: str, password: str, server: str="localhost", port: int=587, protocol: str="STARTTLS", notify_level = 7):
        if type(recipients) is list or type(recipients) is tuple:
            self.recipients = recipients
        elif type(recipients) is str:
            self.recipients = [recipients]
        else:
            self.recipients = [sender]
        self.sender = sender
        self.username = username if username else self.sender
        self.password = password
        self.port = port
        self.server = server
        self.notify_level = notify_level

    def send(self, data: dict):
        subject = f"Backup from {data['source']} to {data['remote']}"
        if data['status'] == 'starting':
            body = f"Backup from {data['source']} to {data['remote']} is starting"
        elif data['status'] == 'complete':
            body = f"Backup from {data['source']} to {data['remote']} has [[result]] in {data['time']}"
            if data['result'] == 0:
                body = body.replace("[[result]]", "completed successfully")
            else:
                body = body.replace("[[result]]", f"errored with status code {data['result']}")

        print(f"Starting connection to SMTP server {self.server}:{self.port}")
        smtp = smtplib.SMTP(self.server, self.port)
        print("Connection started")
        print("Starting TLS")
        smtp.starttls()
        print("TLS Done")
        print("Logging in")
        smtp.login(self.sender, self.password)
        print("Logged in")

        for recipient in self.recipients:
            print("Creating MIME Multipart")
            msg = MIMEMultipart()
            print(f"Setting from field to {self.sender}")
            msg['From'] = self.sender
            print(f"Setting to field to {recipient}")
            msg['To'] = recipient
            print(f"Setting subject field to {subject}")
            msg['Subject'] = subject
            print("Fields set")
            print("Attaching to message")
            msg.attach(MIMEText(body, "plain"))
            print("Attached to message")
            print("Sending mail")
            smtp.sendmail(self.sender, recipient, msg.as_string())
            print("Mail sent")

        smtp.quit()
