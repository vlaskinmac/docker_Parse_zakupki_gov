# -*- coding: utf-8 -*-
import collections
import datetime
import json
import multiprocessing
import random
import re
import threading
import time
from pprint import pprint

import requests
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup

from decorators import time_track, requests_exception
import humanize

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
    return cost


def get_prices_mts(sum_bg, term_days):
    discont = None
    if float(sum_bg) < 50000 and term_days <= 365:
        price_bg = '1500'
    elif 50000 <= float(sum_bg) <= 100000 and term_days <= 365:
        price_bg = '2000'
    elif float(sum_bg) < 50000 and term_days <= 730:
        price_bg = '2500'
    elif 50000 <= float(sum_bg) <= 100000 and term_days <= 730:
        price_bg = '3000'
    elif float(sum_bg) < 50000 and term_days <= 1095:
        price_bg = '3500'
    elif 50000 <= float(sum_bg) < 100000 and term_days <= 1095:
        price_bg = '55000'
    elif 100000 <= float(sum_bg) < 500000:
        rate = 2.9
        price_bg = calculate(sum_bg, term_days, rate)
    elif 500000 <= float(sum_bg) < 1000000:
        rate = 2.8
        price_bg = calculate(sum_bg, term_days, rate)
    elif 1000000 <= float(sum_bg) <= 30000000:
        rate = 2.7
        price_bg = calculate(sum_bg, term_days, rate)
    cost = {
            'name': 'МТС-Банк', 'price_bg': price_bg
        }
    return cost


def get_prices_locko(sum_bg, term_days):
    discont = 0.6
    if float(sum_bg) < 200000:
        price_bg = '6500'
    elif 200000 <= float(sum_bg) < 1000000:
        rate = 3.8
        price_bg = calculate(sum_bg, term_days, rate)
    elif 1000000 <= float(sum_bg) < 10000000:
        rate = 2.3 - discont
        price_bg = calculate(sum_bg, term_days, rate)
    elif 10000000 <= float(sum_bg) < 35000000:
        rate = 2.4 - discont
        price_bg = calculate(sum_bg, term_days, rate)
    cost = {
            'name': 'Локо-Банк', 'price_bg': price_bg
        }
    return cost


def get_prices_uralsib(sum_bg, term_days):
    discont = None
    if float(sum_bg) < 50000:
        rate = 2.7
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1200:
            price_bg = 1200
    elif 50000 <= float(sum_bg) < 100000:
        rate = 2.6
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1200:
            price_bg = 1200
    elif 100000 <= float(sum_bg) < 1000000:
        rate = 2.6
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1500:
           price_bg = 1500
    elif 1000000 <= float(sum_bg) < 10000000:
        rate = 2.45
        price_bg = calculate(sum_bg, term_days, rate)
    elif 10000000 <= float(sum_bg) < 30000000:
        rate = 2.25
        price_bg = calculate(sum_bg, term_days, rate)
    cost = {
            'name': 'Уралсиб', 'price_bg': price_bg
        }
    return cost


def get_prices_soyuz(sum_bg, term_days):
    discont = None
    if 100000 <= float(sum_bg) < 1000000:
        rate = 2.6
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 3000:
            price_bg = 3000
    elif 1000000 <= float(sum_bg) < 15000000:
        rate = 2.6
        price_bg = calculate(sum_bg, term_days, rate)

    cost = {
            'name': 'Банк Союз', 'price_bg': price_bg
        }
    return cost


def get_prices_alef(sum_bg, term_days):
    discont = None
    if float(sum_bg) < 50000:
        rate = 2.3
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1000:
            price_bg = 1000
    elif 50000 <= float(sum_bg) < 100000:
        rate = 2.3
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1000:
            price_bg = 1000
    elif 100000 <= float(sum_bg) < 1000000:
        rate = 2.3
        price_bg = calculate(sum_bg, term_days, rate)
    elif 1000000 <= float(sum_bg) < 18000000:
        rate = 1.8
        price_bg = calculate(sum_bg, term_days, rate)

    cost = {
            'name': 'Алеф Банк', 'price_bg': price_bg
        }
    return cost


def get_prices_keb(sum_bg, term_days):
    discont = None
    if float(sum_bg) < 50000:
        rate = 3
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1000:
            price_bg = 1000
    elif 50000 <= float(sum_bg) < 100000:
        rate = 3
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1000:
            price_bg = 1000
    elif 100000 <= float(sum_bg) < 500000:
        rate = 3
        price_bg = calculate(sum_bg, term_days, rate)
        if price_bg < 1000:
            price_bg = 1000
    elif 500000 <= float(sum_bg) < 1000000:
        rate = 3
        price_bg = calculate(sum_bg, term_days, rate)
    elif 1000000 <= float(sum_bg) < 10000000:
        rate = 2.9
        price_bg = calculate(sum_bg, term_days, rate)
    elif 10000000 <= float(sum_bg) < 35000000:
        rate = 3.5
        price_bg = calculate(sum_bg, term_days, rate)

    cost = {
            'name': 'Кредит Европа Банк', 'price_bg': price_bg
        }
    return cost


def get_prices_kuban(sum_bg, term_days):
    discont = None
    if float(sum_bg) < 100000:
        price_bg = '700'
    elif 100000 <= float(sum_bg) < 50000000:
        rate = 2.3
        price_bg = calculate(sum_bg, term_days, rate)
    cost = {
            'name': 'Кубань Кредит Банк', 'price_bg': price_bg
        }
    return cost


def get_prices_sovkom(sum_bg, term_days):
    discont = None
    if 20000000 < float(sum_bg) < 50000000:
        rate = 3.5
        price_bg = calculate(sum_bg, term_days, rate)
    elif 50000000 <= float(sum_bg) < 500000000:
        rate = 3.25
        price_bg = calculate(sum_bg, term_days, rate)
    cost = {
            'name': 'Совкомбанк', 'price_bg': price_bg
        }
    return cost


def calculate(sum_bg, term_days, rate):
    cost = (float(sum_bg) * rate * term_days / 365) / 100
    return cost.__round__()


@time_track
def main_run(sum_bg, end_date):
    # sum_bg = "800000"
    # end_date = "31.01.2023"
    # end_date = "14.12.2022"

    current_date = datetime.datetime.now()
    datetime_obj = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    term_days_obj = datetime_obj - current_date
    term_days = int(term_days_obj.days)

    costs = []

    goofin = goofinbanks_parse_data(sum_bg, end_date)
    for i in goofin:
        costs.append(
            {
                'name': i['name'], 'price_bg': i['price_bg']
            }
        )
    if float(sum_bg) <= 35000000 and term_days <= 1095:
        cost_mts = get_prices_mts(sum_bg, term_days)
        costs.append(cost_mts)

        cost_locko = get_prices_locko(sum_bg, term_days)
        costs.append(cost_locko)

    if float(sum_bg) <= 30000000 and term_days <= 1200:
        cost_uralsib = get_prices_uralsib(sum_bg, term_days)
        costs.append(cost_uralsib)

    if 100000 <= float(sum_bg) <= 15000000 and term_days <= 1200:
        cost_soyuz = get_prices_soyuz(sum_bg, term_days)
        costs.append(cost_soyuz)

    if float(sum_bg) <= 18000000 and term_days <= 1096:
        cost_alef = get_prices_alef(sum_bg, term_days)
        costs.append(cost_alef)

    if float(sum_bg) <= 35000000 and term_days <= 1825:
        cost_keb = get_prices_keb(sum_bg, term_days)
        costs.append(cost_keb)

    if float(sum_bg) <= 50000000 and term_days <= 1825:
        cost_kuban = get_prices_kuban(sum_bg, term_days)
        costs.append(cost_kuban)

    if 20000000 <= float(sum_bg) <= 500000000 and term_days <= 1850:
        cost_sovkom = get_prices_sovkom(sum_bg, term_days)
        costs.append(cost_sovkom)

    #     print(cost_mts, 'cost_mts')
    # print(costs, '-=-=')

        # "[{'name': 'Почта Банк', 'price_bg': 2855}," \
        # " {'name': 'Сбербанк', 'price_bg': 3019}, " \
        # "{'name': 'Промсвязьбанк', 'price_bg': 4940}," \
        # " {'name': 'СДМ Банк', 'price_bg': 2635}]"

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

    sort_costs = sort_prices(costs)
    return sort_costs

# if __name__ != '__main__':
#     cost = {}

#     sum_bg = '800000'  # на вход
#     end_date = '31.05.2024'  # на вход
#     # costs = main_run(sum_bg, end_date)
#     goofinbanks_parse_data(sum_bg, end_date)
#     # print(costs)


def sort_prices(costs):
    prices = []
    date_entries = collections.defaultdict()
    for i in costs:
        date_entries[int(i['price_bg'])] = i
    done_sort_prices =collections.OrderedDict(sorted(date_entries.items()))
    for i in done_sort_prices.values():
        prices.append(i)
    # pprint(prices)
    return prices
