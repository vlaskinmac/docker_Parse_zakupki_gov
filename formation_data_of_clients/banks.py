# -*- coding: utf-8 -*-
import os
from pprint import pprint

import urllib3

from collections import defaultdict

from itertools import count
from pymongo import MongoClient
from socket import socket
from urllib.parse import urljoin
from requests import ReadTimeout, HTTPError
from urllib3.exceptions import ReadTimeoutError

from crud_base import get_email
from sender_mail import send_email
from render_mail import rebuild
from banks_rates import *
from decorators import requests_exception

import logging.config
import logging.config
from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('proc_1')
# logging.disable(logging.DEBUG)

HOST = 'https://zakupki.gov.ru/'
file_base = 'file_base.csv'
file_mail = 'file_mail.csv'
mail_send = 'file_mail_send.csv'
pre_mail_send = {}
all_info = []


@requests_exception
def headers_random():
    with open("headers", 'r') as file:
        headers_list = file.read()
        headers = str(headers_list).split('\n')
    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head


@requests_exception
def get_contaner_links(session, start_update_date, per_page, price_min, host):
    url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
    head = headers_random()
    payload = {
        "morphology": "on",
        "search-filter": "Дате размещения",
        "sortDirection": "true",
        "recordsPerPage": per_page,
        "showLotsInfoHidden": "false",
        "sortBy": "UPDATE_DATE",
        "fz44": "on",
        "pc": "on",
        "selectedLaws": "FZ44",
        "priceFromGeneral": price_min,
        "currencyIdGeneral": "-1",
        "updateDateFrom": start_update_date,
        "OrderPlacementSmallBusinessSubject": "on",
        "OrderPlacementRnpData": "on",
        "OrderPlacementExecutionRequirement": "on",
        "orderPlacement94_0": 0,
        "orderPlacement94_1": 0,
        "orderPlacement94_2": 0,
        "searchTextInAttachedFile": "Сведения",
        # виды закупок
        # "placingWayList": "EA44,EAP44,EAB44,EAO44,EEA44,OK504,OKP504,OKK504,OKA504,EOK504,OKB504,OKI504,OKU504,OKUP504,"
        #                   "OKUI504,EOKU504,OKUK504"
    }
    # листаем главную страницу
    count_contaner_links = 0
    for page in count(1):
        print(page, '- page')
        payload["pageNumber"] = page
        try:
            response = session.get(url=url, params=payload, headers=head, timeout=3)
            # print(response.url)
        except ReadTimeoutError as exc:
            print(exc)
        soup = BeautifulSoup(response.text, "lxml")
        html_links = []
        # --------------------------------------------------- получили html блок ссылок
        check = soup.select('div .registry-entry__form')
        for i in check:
            chek_error = i.select_one('div .registry-entry__body .error')
            # ---------------------------------проверка на отмену закупки
            if not chek_error:
                html_links.append(i.select_one("div .registry-entry__header-mid__number"))
        # --------------------------------------------------- получили контейнер ссылок
        contaner_links = [urljoin(host, i.select_one("a")["href"]) for i in html_links]
        print(len(contaner_links), '- contaner_links')
        # print(contaner_links, '- contaner_links')
        count_contaner_links += len(contaner_links)
        print(count_contaner_links, "total count_contaner_links")
        print()
        # прерываем  листание главной
        if len(contaner_links) == 0:
            break
        # --------------------------------------------------- получили контейнер номеров закупок
        contaner_links_text = [re.search(r"\b\d+\b", i.text).group() for i in html_links]
        links_contaner = dict(zip(contaner_links, contaner_links_text))
        yield links_contaner


# async здесь создаем tasks

@requests_exception
def get_info_per_tender(session, contaner_links):
    """получает html страницы закупки"""

    count = 0
    for tender_url, number in contaner_links.items():
        head = headers_random()
        count += 1

        # открываем страницу закупки
        try:
            site_tender_response = session.get(url=tender_url, headers=head, timeout=3)
            # site_tender_response.raise_for_status()
            if site_tender_response.ok:
                site_tender_html = BeautifulSoup(site_tender_response.text, 'lxml')
                yield site_tender_html, tender_url, number

        except ReadTimeoutError as exc:
            print(exc)
        except ReadTimeout as exc:
            print(exc)
        except ConnectionError as exc:
            print(exc)
            time.sleep(15)
        except socket.timeout as exc:
            print(exc)
        except urllib3.exceptions.MaxRetryError as exc:
            time.sleep(15)
            print(exc)
        except EOFError as exc:
            print(exc)
        except Exception as exc:
            print(exc)


@requests_exception
def get_price_nmck(site_tender_html):
    """получает НМЦК"""
    price_nmck_html = site_tender_html.select_one('.price .cardMainInfo__content').get_text(strip=True)
    price_nmck = re.sub(r"\xa0", "", price_nmck_html)
    caching['price_nmck'] = float(price_nmck.replace(",", ".").split(" ")[0])
    return caching


@requests_exception
def get_link_orderplan(host, site_tender_html):
    """получает ссылку на Сведения о связи с позицией плана-графика"""
    orderplan_html = site_tender_html.select_one('.blockInfo__section a[href^="/epz/orderplan"]')['href']
    orderplan = urljoin(host, orderplan_html)
    return orderplan


@requests_exception
def get_status_contract(session, site_tender_html, tender_url, tender_number):
    """получает статус контракта"""
    url_ = 'https://zakupki.gov.ru/epz/order/notice/rpec/common-info.html'
    count = 0
    caching['status_contract'] = None
    site_tender_entry_number_response_html = None
    for i in range(1, 4):
        head = headers_random()
        tender_entry_number = tender_number + f"000{i}"
        payload = {
            "regNumber": tender_entry_number
        }
        try:
            site_tender_entry_number_response = session.get(url=url_, params=payload, headers=head, timeout=3)
            site_tender_entry_number_response.raise_for_status()
            if not site_tender_entry_number_response.ok:
                break
            # получаем статус контракта
            site_tender_entry_number_response_html = BeautifulSoup(site_tender_entry_number_response.text, 'lxml')
            status_contract = site_tender_entry_number_response_html.select_one(
                '.cardHeaderBlock + .container .section__info'
            ).get_text(strip=True)
            if status_contract == "Подписание поставщиком":
                count += 1
        except HTTPError as exc:
            pass
        except EOFError as exc:
            print(exc)
        except ReadTimeoutError as exc:
            print(exc)
        except ReadTimeout as exc:
            print(exc)
        except socket.timeout as exc:
            print(exc)
        if count > 2:
            break
    if count == 1:
        caching['tender_number'] = tender_number
        caching['tender_link'] = tender_url
        caching['status_contract'] = "Подписание поставщиком"
        get_price_contract_winner_inn(caching, site_tender_entry_number_response_html, site_tender_html)
        # запуск по многолоту
        # get_price_contract_many_lots(session, site_tender_html, caching)


@requests_exception
def get_price_contract_winner_inn(caching, site_tender_entry_number_response_html, site_tender_html):
    """получает цену контракта и ИНН победителя"""
    caching['price_contract_str'] = \
        site_tender_entry_number_response_html.select('.cardHeaderBlock ~ .container')[2].get_text(strip=True)
    price_contract = re.sub(r"\xa0", "", caching['price_contract_str'])
    try:
        caching['price_contract'] = float(re.search(r"\d+,[0-9]{2}", price_contract).group().replace(",", "."))
        caching['winner_inn_str'] = site_tender_entry_number_response_html.select('.cardHeaderBlock ~ .container')[
            4].get_text(
            strip=True)
    except:
        caching['price_contract_str'] = site_tender_entry_number_response_html.select('.cardHeaderBlock ~ .container')[
            3].get_text(strip=True)
        caching['winner_inn_str'] = site_tender_entry_number_response_html.select('.cardHeaderBlock ~ .container')[
            5].get_text(
            strip=True)
    #  Цена контракта
    price_contract = re.sub(r"\xa0", "", caching['price_contract_str'])
    caching['price_contract'] = float(re.search(r"\d+,[0-9]{2}", price_contract).group().replace(",", "."))
    get_price_nmck(site_tender_html)
    if re.search(r"[0-9]{12}", caching['winner_inn_str']):
        caching['winner_inn'] = re.search(r"[0-9]{12}", caching['winner_inn_str']).group()
    elif re.search(r"[0-9]{10}", caching['winner_inn_str']):
        caching['winner_inn'] = re.search(r"[0-9]{10}", caching['winner_inn_str']).group()
    return caching


# @requests_exception
# def get_price_contract_many_lots(session, site_tender_html, caching):
#     """получает цену контракта и ИНН победителя по многолоту"""
#     logger.debug(f"start -4")
#     print('\nмноголот')
#     head = headers_random()
#     link_protocol_html = site_tender_html.select_one('div .tabsNav a[href*="supplier-results"]')['href']
#     link_protocol = urljoin(host, link_protocol_html)
#     site_protocol_response = session.get(url=link_protocol, headers=head, timeout=3)
#     site_protocol_response.raise_for_status()
#     if site_protocol_response.ok:
#         site_protocol_html = BeautifulSoup(site_protocol_response.text, 'lxml')
#         site_protocol = site_protocol_html.select('.cardHeaderBlock ~ .container')[0].get_text(strip=True)
#         site_protocol_clean_1 = re.sub(r"[\xa0|\s]", "", site_protocol)
#         site_protocol_clean_2 = re.search(r"Победитель\d+,[0-9]{2}", str(site_protocol_clean_1)).group()
#         if site_protocol_clean_2:
#             price_contract = re.sub(r"[А-аЯ-я]", "", site_protocol_clean_2).replace(",", ".")
#             caching['price_contract'] = float(price_contract)
#         get_price_nmck(site_tender_html)
#     return caching


@requests_exception
def get_summ_bg(site_tender_html, caching):
    """получает сумму бг"""

    try:
        summ_bg_tags = site_tender_html.select_one('div #custReqNoticeTable').select('.section__info')
    except Exception as exc:
        print(exc)
    caching['demping'] = None
    demping = 100 - (caching['price_contract'] / caching['price_nmck'] * 100)
    if demping.__round__(2) > 25:
        caching['demping'] = demping.__round__(2)
    for i in summ_bg_tags:
        summ_bg_prev_clean_1 = re.sub(r"[\xa0\s]", "", i.text.strip())
        try:
            try:
                summ_bg_prev_2 = re.search(r"(\d+,[0-9]{2}₽)|([0-9]{1,2}%)", summ_bg_prev_clean_1).group()
                get_summ_bg_and_precentage(summ_bg_prev_2, caching)
            except Exception:
                summ_bg_prev_3 = re.search(r"[0-9]{1,2}%", summ_bg_prev_clean_1).group()
                get_summ_bg_and_precentage(summ_bg_prev_3, caching)
        except AttributeError as exc:
            pass


@requests_exception
def get_summ_bg_and_precentage(summ_bg_prev_2, caching):
    summ_bg_and_precentage = re.sub(r"[₽%]", "", summ_bg_prev_2)
    # Сумма бг по ст.96
    if re.search(r"%", summ_bg_prev_2):
        if not caching['demping']:
            caching['summ_bg'] = (
                    caching['price_contract'] * (float(summ_bg_and_precentage) / 100).__round__(2)).__round__(2)
        else:
            caching['summ_bg'] = (caching['price_contract'] * (float(summ_bg_and_precentage) / 100) * 1.5).__round__(2)
    # Сумма бг не ст.96
    if re.search(r"₽", summ_bg_prev_2):
        if not caching['demping']:
            caching['summ_bg'] = float(summ_bg_and_precentage.replace(",", "."))
        else:
            caching['summ_bg'] = (float(summ_bg_and_precentage.replace(",", ".")) * 1.5).__round__(2)
    return caching


@requests_exception
def get_term_contract(session, orderplan):
    """получает срок контракта"""

    head = headers_random()
    site_orderplan = session.get(url=orderplan, headers=head, timeout=3)
    site_orderplan.raise_for_status()
    if site_orderplan.ok:
        site_orderplan_html = BeautifulSoup(site_orderplan.text, 'lxml')
        # Блок заголовка таблицы с графиком финансирования
        dates_orderplan_html = site_orderplan_html.select(
            '.blockInfo__table thead th[class*="tableBlock__col tableBlock__col_header tableBlock__col_right"]'
        )
        # Блок тела таблицы с суммами финансирования
        sum_orderplan_html = site_orderplan_html.select(
            '.blockInfo__table tbody td[class*="tableBlock__col tableBlock__col_right"]'
        )
        for i, value in enumerate(dates_orderplan_html):
            date_orderplan = re.search(r"[0-9]{4}", value.text.strip())
            sum_orderplan = re.sub(r"[\xa0|\s]", "", sum_orderplan_html[i].text.strip().replace(",", ""))
            if date_orderplan and int(sum_orderplan) > 1:
                caching['term_contract'] = f'31.01.{int(date_orderplan.group()) + 1}'
        return caching


def bubble_sort_price(prices):
    # Устанавливаем swapped в True, чтобы цикл запустился хотя бы один раз
    swapped = True
    while swapped:
        swapped = False
        # for u in y:
        for i in range(len(prices) - 1):
            if prices[i]['price_bg'] > prices[i + 1]['price_bg']:
                # Меняем элементы
                prices[i]['price_bg'], prices[i + 1]['price_bg'] = prices[i + 1]['price_bg'], prices[i]['price_bg']
                # Устанавливаем swapped в True для следующей итерации
                swapped = True
    return prices


def get_result_collect_parametres(collect_parametres, caching):
    try:
        # lock = threading.Lock()
        # with lock:
        time.sleep(0.1)
        collect = {
            "winner_inn": caching['winner_inn'],
            "price_nmck": caching['price_nmck'],
            "price_contract": caching['price_contract'],
            "term_contract": caching['term_contract'],
            "tender_link": caching['tender_link'],
            'tender_number': caching['tender_number'],
            "summ_bg": caching['summ_bg'],
            "email_address": mail,
            "full_name": full_name,
            "short_name": short_name,
            "banks_prices": None,
            "phone": phone,
            "email_content": None,
        }
        if collect:
            # logger.debug(
            #     f" --final collect {caching['winner_inn']}, {caching['price_nmck']}, {caching['price_contract']},"
            #     f" {caching['term_contract']}, {caching['summ_bg']},"
            #     f" {mail} {caching['tender_link']}")
            summ = str(caching['summ_bg'].__round__())
            coll = main_run(summ, caching['term_contract'])
            if coll:
                collect_parametres[caching['winner_inn']].append(collect)
                banks_prices = bubble_sort_price(coll)
                collect_parametres[caching['winner_inn']][0]["banks_prices"] = banks_prices
                # print("==================================================================",collect_parametres)
                # срендернное письмо

                letter_html = rebuild(collect_parametres)
                collect_parametres[caching['winner_inn']][0]["email_content"] = letter_html

            else:
                logger.warning(
                    f"- {caching['winner_inn']} - {caching['tender_number']} - no price")
                print('no price - ', caching['tender_link'])
        else:
            print('no collect - ', caching['tender_link'])
    except HTTPError as exc:
        logger.warning(f'HTTPError - {exc}')
    except Exception as exc:
        logger.debug(f"-----ERROR end -88888--  {exc}--")
    return collect_parametres


def write_letter_db(result_collect_parametres, MONGO_URL):
    """ запись в mongo """

    cluster = MongoClient(MONGO_URL)
    cluster.time_zone = 'Moscow'

    db = cluster["sent_letter_db"]
    collection = db["sent_letters"]

    for entire in result_collect_parametres.values():
        full_collect_parametres = {
                "_id": random.randint(1, 4000),
                "winner_inn": entire[0]["winner_inn"],
                "full_name": entire[0]["full_name"],
                "short_name": entire[0]["short_name"],
                "price_nmck": entire[0]["price_nmck"],
                "price_contract": entire[0]["price_contract"],
                "term_contract": entire[0]["term_contract"],
                "tender_link": entire[0]["tender_link"],
                "tender_number": str(entire[0]["tender_number"]),
                "summ_bg": entire[0]["summ_bg"],
                "email_address": entire[0]["email_address"],
                "phone": entire[0]["phone"],
                "banks_prices": entire[0]["banks_prices"],
                "email_content": entire[0]["email_content"],
                "create_datetime": datetime.datetime.now(),
                "create_date": datetime.datetime.today(),
                "flag_resending_and_delete_email": None,
            }
    try:
        if not collection.count_documents({"tender_number": full_collect_parametres["tender_number"]}):
            print("отправка письма\n")

            if collection.count_documents({"_id": full_collect_parametres["_id"]}):
                full_collect_parametres["_id"] = random.randint(4001, 8000)
            try:
                collection.insert_one(full_collect_parametres)
                print("записано! монго")
                print()
                # отправка письма
                # send_email(full_collect_parametres)
                collection.update_one({"_id":full_collect_parametres["_id"]}, {full_collect_parametres["flag_resending_and_delete_email "]: 1})
            except Exception as exc:
                print(exc, " --- MONGO EXC")
                # print("result_collect_parametres:")
                # pprint(result_collect_parametres)
                # print("full_collect_parametres:")
                # pprint(full_collect_parametres)
                # print(len(result_collect_parametres), "len-2")
            print("\nПисьмо отправлено!\n")

        else:
            tender_number = collection.find_one({"_id": full_collect_parametres["_id"]})["tender_number"]
            print(tender_number, ' +++++++ тендер уже существует ------mongo +++')
    except Exception as exc:
        print(exc, " --- MONGO EXC --2")


if __name__ == "__main__":
    semaphore = threading.Semaphore(1)
    caching = {}
    collect_parametres = defaultdict(list)
    MONGO_URL = os.environ.get('MONGO_URL')
    host = "https://zakupki.gov.ru"
    session = requests.Session()
    auth_ = HTTPProxyAuth("Seltesseractmaks", "R6l3EhG")
    proxy = {"http": 'http://185.29.127.235:45785'}
    session.proxies = proxy
    session.auth = auth_

    start_update_date = '01.06.2022'
    per_page = 50
    price_min = '1000000'
    count_total = 0
    count_status_ok = 0
    count_status_no = 0
    count_mail_ok = 0
    count_commom_exc = 0
    count_mongo_exc = 0

    for contaner_links in get_contaner_links(session, start_update_date, per_page, price_min, host):
        try:
            obj = get_info_per_tender(session, contaner_links)
        except:
            continue
        for site_tender_html, tender_url, tender_number in obj:
            get_status_contract(session, site_tender_html, tender_url, tender_number)
            count_total += 1
            if caching['status_contract']:
                count_status_ok += 1
                lock = threading.Lock()
                with lock:
                    # здесь create acync tasks
                    try:
                        # получаем контакты из базы
                        full_name, short_name, phone, mail = get_email(caching['winner_inn'])
                        count_mail_ok += 1
                        orderplan = get_link_orderplan(host, site_tender_html)
                        if orderplan:
                            get_term_contract(session, orderplan)
                            get_summ_bg(site_tender_html, caching)
                            result_collect_parametres = get_result_collect_parametres(collect_parametres, caching)
                            caching = {}
                            # запись в mongo
                            write_letter_db(result_collect_parametres, MONGO_URL)
                            collect_parametres = defaultdict(list)
                        else:
                            count_commom_exc += 1
                            print("commom_exc:")
                            print(result_collect_parametres)
                            collect_parametres = defaultdict(list)
                            print()
                            print(len(result_collect_parametres), 'total rows - collect_parametres')
                            print('count_mail_ok -', count_mail_ok)
                            print('count_status_ok - ', count_status_ok)
                            print('count_total - ', count_total)
                            print()
                    except:
                        print('KeyError: winner_inn', tender_url)
                        print()
                        print(caching['winner_inn'])
                        print()
                        # print('KeyError: winner_inn\n' * 5, tender_url)
            else:
                count_status_no += 1
                count_commom_exc += 1

        # pprint(result_collect_parametres)

        print()
        print(len(result_collect_parametres), 'total rows - collect_parametres')
        print('count_mail_ok -', count_mail_ok)
        print('count_status_ok - ', count_status_ok)
        print('count_total - ', count_total)
        print()
        print('count_commom_exc - ', count_commom_exc)
        print('count_count_mongo_exc_exc - ', count_mongo_exc)
        print("-"*70)
        print()
        if count_total > 5000:
            print('count_total - ', count_total)
            print('count_status_ok - ', count_status_ok)
            print('count_mail_ok -', count_mail_ok)
            break
