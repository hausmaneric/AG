from typing import Any, overload
import smtplib
from email.message import EmailMessage
from Class.nextbase import *

class Email(NXBase):
    assunto  : str
    body     : str
    to       : str 
    def __init__(self) -> None:        
        self.assunto   = None
        self.body      = None

def sendEmail(email: Email):
    assunto         = email.assunto
    body            = email.body
    to              = email.to
    email_address   = 'eric.hausman.m@gmail.com'
    email_password  = 'xdwbsvcwrqrpnufo'

    msg = EmailMessage()
    msg['Subject']  = assunto
    msg['From']     = email_address
    msg['To']       = to
    password        = email_password
    msg.add_header('Content-type', 'text/html')
    msg.set_content(body)
    
    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    
    return {"msg":"Email enviado"}