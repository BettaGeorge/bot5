# email.py
# extension to enable sending emails to people
# TODO: my pw shouldn't be in here in plaintext ...

import bot5utils
from bot5utils import *
from bot5utils import ext as b5

import smtplib,ssl
from email.mime.text import MIMEText

class Email:
    def __init__(self):
        pass

    # WARNING: while I have managed to allow unicode characters (such as äöüß) in the message body, unicode in the subject line or sender or receiver might still cause problems.
    def send(self, to: str, subject: str, msg: str):
        port = 465
        smtp_server='smtp.uni-kl.de'
        sender_user = "rettich@rhrk.uni-kl.de"
        sender_email = "fs.leo@mathematik.uni-kl.de"
        password = "foo" # TODO: load via dotenv
        mailcontext = ssl.create_default_context()

        messagecontent = MIMEText(msg.encode('utf-8'),_charset='utf-8')
        messagecontent['Subject'] = subject
        messagecontent['From'] = sender_email
        messagecontent['To'] = to
        with smtplib.SMTP_SSL(smtp_server,port,context=mailcontext) as mailserver:
            mailserver.login(sender_user,password)
            mailserver.sendmail(sender_email,to,messagecontent.as_string())

def setup(bot):
    b5('ext').register('email',Email())

def teardown(bot):
    b5('ext').unregister('email')
