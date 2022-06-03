# -*- coding: utf-8 -*-
import datetime
import json
import multiprocessing
import random
import re
import threading
import time


import requests
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup

from decorators import time_track, requests_exception

@requests_exception
def headers_random():
    with open("headers", 'r') as file:
        headers_list = file.read()
        headers = str(headers_list).split('\n')
    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head


def goofinbanks_getting_data(sum_bg, end_date):
    """
    Почта Банк - 99,
    Сбербанк - 94,
    Банк-РГС - 92,
    Промсвязьбанк - 84
    """

    filename = 'ttt.txt'
    url_goodfin = "https://goodfin.ru/calculator_get_results.php"
    session = requests.Session()
    auth_ = HTTPProxyAuth("Seltesseractmaks", "R6l3EhG")
    proxy = {"http": 'http://185.29.127.235:45785'}
    session.proxies = proxy
    session.auth = auth_
    head = headers_random()
    start_date_pre = datetime.datetime.now()
    end_date_pre = datetime.datetime.strptime(end_date, '%d.%m.%Y')
    period_pre = end_date_pre - start_date_pre
    period = str(period_pre.days)
    payload = {
        "fz": "54",
        "product": "62",
        "cost": sum_bg,
        "days": period,
        "callback": "calcSearchCallback",
    }
    time.sleep(1)
    base_html_code = session.get(url_goodfin, params=payload, headers=head, timeout=3)
    soup = BeautifulSoup(base_html_code.text, 'lxml')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(soup.text)
    with open(filename, 'r', encoding='utf-8') as file:
        text_var = file.read()
    return text_var


def goofinbanks_parse_data(sum_bg, end_date):
    cost = []

    text_var = goofinbanks_getting_data(sum_bg, end_date)
    get_tid = re.search(r'\({"[\d]{2}"', text_var).group()
    parse_data_pre = text_var[text_var.find(f'{get_tid}') + 1:]

    parse_data = parse_data_pre[:-1]
    data_json = json.loads(parse_data)
    # pprint(data_json)

    if int(sum_bg) < 30000000:
        cost.append(
            {
                'name': data_json['99']['bank']['name'], 'price_bg': data_json['99']['cost']
            }
        )
    if int(sum_bg) < 50000000:
        cost.append(
            {
                'name': data_json['94']['bank']['name'], 'price_bg': data_json['94']['cost']
            }
        )
    if int(sum_bg) < 50000000:
        cost.append(
            {
                'name': data_json['84']['bank']['name'], 'price_bg': data_json['84']['cost']
            }
        )
    if int(sum_bg) < 10000000:
        cost.append(
            {
                'name': data_json['101']['bank']['name'], 'price_bg': data_json['101']['cost']
            }
        )
    return cost

    # cost = {
    #     data_json['99']['bank']['name']: data_json['99']['cost'],
    #     data_json['94']['bank']['name']: data_json['94']['cost'],
    #     data_json['92']['bank']['name']: data_json['92']['cost'],
    #     data_json['84']['bank']['name']: data_json['84']['cost'],
    #     data_json['101']['bank']['name']: data_json['101']['cost'],
    # }

    # print(data_json['99']['bank']['name'], data_json['99']['cost'], sep=': ')
    # print(data_json['94']['bank']['name'], data_json['94']['cost'], sep=': ')
    # print(data_json['92']['bank']['name'], data_json['92']['cost'], sep=': ')
    # print(data_json['84']['bank']['name'], data_json['84']['cost'], sep=': ')
    # print(data_json['101']['bank']['name'], data_json['101']['cost'], sep=': ')


@time_track
def main_run(sum_bg, end_date):
    costs = []
    goofin = goofinbanks_parse_data(sum_bg, end_date)
    for i in goofin:
        # for bank_name, price_bg in i:
        costs.append(
            {
                'name': i['name'], 'price_bg': i['price_bg']
            }
        )

    # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    # sovkom = pool.apply_async(sovcom_bank, [sum_bg, end_date])
    # loko = pool.apply_async(loko_bank, [sum_bg, end_date])
    # mts = pool.apply_async(mts_bank, [sum_bg, end_date])
    # alfa = pool.apply_async(alfa_bank, [sum_bg, end_date])
    # uralsib = pool.apply_async(uralsib_bank, [sum_bg, end_date])
    # time.sleep(0.1)
    # pool.close()
    # pool.join()
    # time.sleep(0.3)
    # # print(costs)
    # for i in [sovkom, mts, loko, uralsib, alfa]:
    #     costs.append(i.get(timeout=1))
    return costs

# if __name__ != '__main__':
#     cost = {}

#     sum_bg = '800000'  # на вход
#     end_date = '31.05.2024'  # на вход
#     # costs = main_run(sum_bg, end_date)
#     goofinbanks_parse_data(sum_bg, end_date)
#     # print(costs)
