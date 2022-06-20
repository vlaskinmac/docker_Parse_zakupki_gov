# -*- coding: utf-8 -*-

import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validate import validate

import logging.config
from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('proc_1')


def send_email(entire_id):
    """
     return:
         '200' - успешная отправка
         '404' - адрес не валиден
         '400' - общая ошибка при отправке письма
    """
    try:
        getter = 'kangelina86@mail.ru'
        # getter = 'vlaskinmak@yandex.ru'
        # getter = 'tesseractmaks@gmail.com'

        # getter = entire_id['email_address']

        if validate(
                email_address=getter,
                check_format=True,
                check_blacklist=False,
                check_dns=True,
                dns_timeout=10,
                check_smtp=True,
                smtp_debug=False
        ):
            time.sleep(1)
            sender = 'clients@offenbach-debussy.ru'
            server = smtplib.SMTP('smtp.offenbach-debussy.ru', 25)
            server.ehlo()
            server.starttls()
            # subject = "({})₽ Комиссия: {} руб. за бг по закупке: № {} кешбэк 15% от счета".format(entire_id['email_address'], entire_id['best_price'], entire_id['tender_number'])
            subject = f"₽ Комиссия: {entire_id['best_price']} руб. за бг по закупке: № {entire_id['tender_number']} кешбэк 15% от счета"
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
                return "No file"
            server.sendmail(sender, getter, msg.as_string())
            logger.debug("{} - письмо отправлено\n".format(getter))
            return "200"
        else:
            logger.debug("{} - адрес не валиден\n".format(getter))
            return "404"
    except Exception as exc:
        logger.debug("{} ошибка при отправке письма\n".format(exc))
        return "400"


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
