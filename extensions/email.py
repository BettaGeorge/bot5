# BOT5 EXTENSION
# email.py
# extension to enable sending emails to people

#----------------------------------------------------------------------------
#"THE COFFEEWARE LICENSE":
#Adrian Rettich (adrian.rettich@gmail.com) wrote this file. As long as you retain this notice, you can do whatever you want with this stuff. If we should meet in person some day, and you think this stuff is worth it, you are welcome to buy me a coffee in return.  
#----------------------------------------------------------------------------



import bot5utils
from bot5utils import *
from bot5utils import ext as b5

import smtplib,ssl
from email.mime.text import MIMEText

class Email:
    def __init__(self):
        pass

    # WARNING: while I have managed to allow unicode characters (such as äöüß) in the message body, unicode in the subject line or sender or receiver might still cause problems.
    # to is either an email address or a UserClass object.
    def send(self, to, subject: str, msg: str):
        receiver = to
        if not isinstance(to,str):
            receiver = to.get('rhrk')+'@rhrk.uni-kl.de'
        port = 465
        smtp_server='smtp.uni-kl.de'
        sender_user = b5config['email']['smtp user']
        sender_email = b5config['email']['from']
        password = b5secret['email']['smtp pass']
        mailcontext = ssl.create_default_context()

        messagecontent = MIMEText(msg.encode('utf-8'),_charset='utf-8')
        messagecontent['Subject'] = subject
        messagecontent['From'] = sender_email
        messagecontent['To'] = receiver
        with smtplib.SMTP_SSL(smtp_server,port,context=mailcontext) as mailserver:
            mailserver.login(sender_user,password)
            mailserver.sendmail(sender_email,receiver,messagecontent.as_string())

def setup(bot):
    b5('ext').register('email',Email())

def teardown(bot):
    b5('ext').unregister('email')
