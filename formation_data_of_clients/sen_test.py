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

import logging.config
from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('proc_1')


def sen_email():
    try:

        #text = "hello"

        # user = 'kangelina86@mail.ru'
        # password = 'Vfrcvfrc11'
        # password = '0RKP0MuSi9mumZzk7nja'
        # password = 'Vfrcvfrc1'



        #sender = 'client@offenbach-debussy.ru'
        sender = 'clients@offenbach-debussy.ru'
        # getter = 'vlaskinmak@yandex.ru'
        #getter = 'kangelina86@mail.ru'
        #getter = 'tesseractmaks@gmail.com'

        #getter = full_collect_parametres['email_address']

        server = smtplib.SMTP('smtp.offenbach-debussy.ru', 25)
        server.ehlo()
        server.starttls()


        #msg = MIMEText(text)
        # server.login(sender, password)
        # server.login('user', password)

        # subject = "({})₽ Комиссия: {} руб. за бг по закупке: № {} кешбэк 15% от счета".format(full_collect_parametres['email_address'], full_collect_parametres['best_price'], full_collect_parametres['tender_number'])
        # subject = f"₽ Комиссия: {full_collect_parametres['best_price']} руб. за бг по закупке: № {full_collect_parametres['tender_number']} кешбэк 15% от счета"
        # getter = full_collect_parametres['email_address']
        subject = '999'
        getter = 'kangelina86@mail.ru'
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

        try:
            with open('index.html') as file:
                template = file.read()
                msg.attach(MIMEText(template, 'html'))
        except IOError:
            logger.debug("нет шаблона письма\n")
        print("+++++++")

        server.sendmail(sender, getter, msg.as_string())
    except Exception as exc:
        logger.debug("{} ошибка при отправке письма\n".format(exc))

sen_email()
    # -------------------------------------------------прогрев:

    # count = 0
    # for i in range(1000):
    #     time.sleep(10)
    #     count += 1
    #     try:
    #         with open('index.html') as file:
    #             template = file.read()
    #             msg.attach(MIMEText(template, 'html'))
    #     except IOError:
    #         return "No file"
    #
    #     server.sendmail(sender, getter, msg.as_string())
    #     print(getter, count)
