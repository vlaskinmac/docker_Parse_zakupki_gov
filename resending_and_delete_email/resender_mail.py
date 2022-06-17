# -*- coding: utf-8 -*-
import csv
import re
import smtplib
import ssl
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename


def send_email():
    # text = "hello"

    # user = 'kangelina86@mail.ru'
    # password = 'Vfrcvfrc11'
    # password = '0RKP0MuSi9mumZzk7nja'
    # password = 'Vfrcvfrc1'

    # sender = 'user@testtesseract.ru'
    # sender = 'client@offenbach-debussy.ru'
    sender = 'clients@offenbach-debussy.ru'
    # getter = 'vlaskinmak@yandex.ru'
    # getter = 'kangelina86@mail.ru'
    # getter = 'tesseractmaks@gmail.com'

    # getters = ['tesseractmaks@gmail.com', 'kangelina86@mail.ru','vlaskinmak@yandex.ru']
    getters = ['kangelina86@mail.ru', 'tesseractmaks@gmail.com']
    server = smtplib.SMTP('smtp.offenbach-debussy.ru', 25)
    # server = smtplib.SMTP('smtp.testtesseract.ru', 25)
    server.ehlo()
    server.starttls()

    # msg = MIMEText(text)
    # server.login(sender, password)
    # server.login('user', password)

    subject = 'First test mail'
    msg = MIMEMultipart()
    msg['Content-Type'] = 'text/html', 'text/plain'
    msg['Subject'] = subject
    msg['From'] = sender
    msg['Cc'] = ''
    msg['Reply-To'] = sender
    # msg['To'] = getter
    msg['Return-Path'] = sender
    msg['Feedback-ID'] = 'CampaignIDX:CustomerID2:MailTypeID3:66SenderId'

    msg['List-Unsubscribe'] = '<mailto:complaint@offenbach-debussy.ru?subject=unsubscribe>'
    for getter in getters:
        msg['To'] = getter
        count = 0
        for i in range(1000):
            time.sleep(10)
            count += 1
            try:
                with open('index.html') as file:
                    template = file.read()
                    msg.attach(MIMEText(template, 'html'))
            except IOError:
                return "No file"

            server.sendmail(sender, getter, msg.as_string())
            print(getter, count)


# send_email()
