# -*- coding: utf-8 -*-
import random
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import logging.config
from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('proc_1')


def send_email():

    try:
        getter = 'kangelina86@mail.ru'
        # getter = 'vlaskinmak@yandex.ru'
        # getter = 'tesseractmaks@gmail.com'

        # getter = entire_id['email_address']

        time.sleep(1)
        sender = 'clients@offenbach-debussy.ru'
        server = smtplib.SMTP('smtp.offenbach-debussy.ru', 25)
        server.ehlo()
        server.starttls()
        # subject = "({})₽ Комиссия: {} руб. за бг по закупке: № {} кешбэк 15% от счета".format(entire_id['email_address'], entire_id['best_price'], entire_id['tender_number'])
        subject = f"{random.randint(1, 1000)}Комиссия"
        msg = MIMEMultipart()
        msg['Content-Type'] = 'text/html', 'text/plain'
        msg['Subject'] = subject
        msg['From'] = sender
        msg['Cc'] = ''
        msg['Reply-To'] = sender
        msg['To'] = getter
        msg['Return-Path'] = sender
        msg['Feedback-ID'] = 'CampaignIDX:CustomerID2:MailTypeID3:66SenderId'
        msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
        msg['List-Unsubscribe'] = '<mailto:complaint@offenbach-debussy.ru?subject=unsubscribe>'
        msg['Precedence'] = 'bulk'

        server.sendmail(sender, getter, msg.as_string())

        count = 0
        for i in range(10000):
            time.sleep(7)
            count += 1
            try:
                with open('index.html') as file:
                    template = file.read()
                    msg.attach(MIMEText(template, 'html'))
            except IOError as exc:
                logger.debug(f"{exc}")

            server.sendmail(sender, getter, msg.as_string())
            logger.debug("{} -{} грев отправлено\n".format(getter, count))
    except Exception as exc:
        logger.debug("{} ошибка при отправке письма\n".format(exc))


send_email()


