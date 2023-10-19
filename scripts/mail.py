import argparse
import csv
import smtplib
import ssl
import os
from email.message import EmailMessage

parser = argparse.ArgumentParser()
parser.add_argument('--subscribers', required=True) # Subscribers CSV
parser.add_argument('--subject', required=True) # Literal
parser.add_argument('--message', required=True) # File
args = parser.parse_args()

sender_email = 'phil@eatonphil.com'
smtp_server = 'mail.privateemail.com'
port = 587
password = os.getenv("NPP")

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.starttls(context=context)
    server.login(sender_email, password)

    with open("sent.log", "w") as sentlog:
        with open(args.subscribers, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                who = row["Subscriber"]
                message = EmailMessage()
                message["Subject"] = args.subject
                message["From"] = f"Phil Eaton <{sender_email}>"
                message["To"] = who
                with open(args.message) as f:
                    message.set_content(f.read(), subtype="html")
                server.send_message(message)
                sentlog.write(who+"\n")
