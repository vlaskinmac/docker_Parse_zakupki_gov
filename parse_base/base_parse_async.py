import asyncio
import logging.config
import multiprocessing

from logging_config import dict_config

logging.config.dictConfig(dict_config)

import datetime
import math
import random

import re
import os

import time
from multiprocessing import Pool, cpu_count

from urllib.parse import urljoin

import aiofiles
import aiohttp
import requests

from bs4 import BeautifulSoup
from datetime import timedelta
from dotenv import load_dotenv
from itertools import count

from requests import HTTPError, ReadTimeout
from requests.auth import HTTPProxyAuth

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# participantType_2 - ИП, participantType_0 - юр. лица
# url = "https://zakupki.gov.ru/epz/eruz/search/results.html?morphology=on&" \
#       "search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&" \
#       "pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=BY_REGISTRY_DATE&" \
#       "participantType_0=on&participantType_2=on&participantType=0%2C2&registered=on&" \
#       "rejectReasonIdNameHidden=%7B%7D&countryRegIdNameHidden=%7B%7D"

# url2 = "https://zakupki.gov.ru/epz/eruz/search/results.html?&pageNumber=10&recordsPerPage=_500&participantType=0%2C2&registryDateFrom=01.04.2021&registryDateTo=14.04.2021"
from orm_models import Lids
# logger = logging.getLogger("check")

postgres_url = os.environ.get('ENGINE')
engine = create_engine(postgres_url)

# engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session_base = Session()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/96.0.4{}.{} Safari/537.36",

}


def prepare_period_start_segment(start_date_str):
    date_time_obj = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    prepare_today_date_obj = datetime.datetime.today()
    prepare_period_obj = prepare_today_date_obj - date_time_obj
    prepare_start_segment_date_obj = prepare_today_date_obj - timedelta(days=prepare_period_obj.days)
    return prepare_start_segment_date_obj


# получаем страниц всего на отрезке
def get_total_pages(response, per_page):
    soup = BeautifulSoup(response.text, "lxml")
    prepare_total_pages = soup.select_one(".search-results__total").get_text(strip=True)
    total_pages = re.sub(r"[^\d+]", "", prepare_total_pages)
    pages = (int(total_pages) + 1) / per_page
    return math.ceil(pages)


def get_content_by_segments(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN):
    global count_line
    session = requests.Session()

    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    auth_ = HTTPProxyAuth(PROXY_LOGIN, PROXY_PASS)
    proxy = {"http": PROXY_IP}
    session.proxies = proxy
    session.auth = auth_


    # print(total_pages)
    url = "https://zakupki.gov.ru/epz/eruz/search/results.html"
    payload = {
        "pageNumber": page,
        "recordsPerPage": per_page,
        "participantType": "0,2",
        "registered": "on",

    }

    for segment in count(step=14):
        start_s = time.time()
        start_segment_date_obj = prepare_start_segment_date_obj + timedelta(days=period_segment + segment)
        end_segment_date_obj = start_segment_date_obj + timedelta(days=period_segment - 1)
        start_segment_date = datetime.datetime.strftime(start_segment_date_obj, '%d.%m.%Y')
        end_segment_date = datetime.datetime.strftime(end_segment_date_obj, '%d.%m.%Y')
        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date
        try:
            response = session.get(url, params=payload, headers=headers, timeout=3)
            response.raise_for_status()
            total_pages = get_total_pages(response, per_page)
            name_process = multiprocessing.current_process().name
            print(
                f'====================================== process {name_process[-1:]} ================================================')
            print('start_segment_date - end_segment_date', start_segment_date, '-', end_segment_date)
            print(total_pages, '--total_pages of segment')
            # print(response.url)
            logger.warning(f"\n new segment ======= {start_segment_date} --- {end_segment_date} =======\n")
        except ReadTimeout as exc:
            logger.warning(f"{exc}")
        except HTTPError as exc:
            logger.warning(f"{exc}")
        except ConnectionError as exc:
            logger.warning(f"{exc}")
            time.sleep(15)
        except OSError as exc:
            logger.warning(f"{exc}")
        except Exception as exc:
            logger.warning(f"{exc} --")

        for num_page in count(1):
            count_line = 0
            start_p = time.time()
            payload["pageNumber"] = num_page
            try:
                response = session.get(url, params=payload, headers=headers, timeout=3)
                response.raise_for_status()
                # print(response.url)

                print(num_page, '-- current num_page \n')
                if num_page > total_pages:
                    break
                yield response
                print('process--', name_process[-1:], '---------------time page-------:',time.time() - start_p, '\n')

            except ReadTimeout as exc:
                logger.warning(f"{exc}")
            except HTTPError as exc:
                logger.warning(f"{exc}")
            except ConnectionError as exc:
                logger.warning(f"{exc}")
                time.sleep(15)
            except OSError as exc:
                logger.warning(f"{exc}")
            except Exception as exc:
                logger.warning(f"{exc} --")
            # print(response.url)

        print('-' * 40)
        name_process = multiprocessing.current_process().name
        print('process--', name_process[-1:], time.time() - start_s, '-----time of done segment-----', start_segment_date, '-', end_segment_date, '\n')


        # if end_segment_date_obj > datetime.datetime.today():

        if end_segment_date_obj > datetime.datetime.strptime(end_date, '%d.%m.%Y'):
            print(end_date, '-end_date****** --- end process --- ******** process--', name_process[-1:])
            logger.warning(f"\n{end_date} -end_date****** --- end process --- ******** process-- {name_process[-1:]}")

            # if end_segment_date > "05.04.2019":
            break


def get_links_by_segments(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN):
    global count_links_total
    global count_total_new_email
    # --------------------------------------------------- получили html страницу c контейнером ссылок c одной страницы
    links = get_content_by_segments(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN)
    for link_text in links:
        soup = BeautifulSoup(link_text.text, "lxml")
        prepare_contaners = soup.select("div.search-registry-entry-block")

        host = "https://zakupki.gov.ru"
        # --------------------------------------------------- получили пулл ссылок

        contaner_links = [
            urljoin(host, i) for i in [link.select_one("div.registry-entry__body-href a")["href"]
                                       for link in prepare_contaners]
        ]
        name_process = multiprocessing.current_process().name
        print('process--', name_process[-1:], '-------', len(contaner_links), '-- contaner_links\n')
        count_links_total += len(contaner_links)



        # print(contaner_links)
        yield contaner_links


async def headers_random():
    async with aiofiles.open("headers", 'r') as file:
        # proxies=file.read().split('\n')
        headers_list = await file.read()

        headers = str(headers_list).split('\n')

    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head
# async def rand_sleep():
#    return await asyncio.sleep(random.randint(0, 1))


async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):
    # async def interface_of_paths_ip_ooo(session, link, auth, proxy_):
    global count_line_total
    global count_links_total
    global count_line



    # head = {
    #     "User-Agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                   f"Chrome/96.0.4{random.randint(10, 463)}4.{random.randint(10, 110)} Safari/537.36",
    #
    # }
    # head = {
    #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    #
    # }

    # head = {
    #     "User-Agent": "*"
    #
    # }

    # async with aiofiles.open("proxy_clean", 'r') as file:
    # proxies_str = await file.read()
    # proxies_str = ['http://58.27.59.249:80', 'http://107.151.182.247:80', 'http://169.57.1.85:8123']
    # proxy_ = random.choice(proxies_str)

    # rand = random.randint(3, 15)

    await asyncio.sleep(random.randint(0, 1))
    # await rand_sleep()

    async with semaphore:
        head = await headers_random()
        # print(head)
        try:
            await asyncio.sleep(random.randint(0, 1))
            # async with session.get(url=link, proxy_auth=auth, ssl=False, timeout=rand, proxy=proxy_, headers=head) as response:
            async with session.get(url=link, proxy_auth=auth, ssl=False, proxy=proxy_, headers=head) as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                # print(soup)
                contaner_html = soup.select(".blockInfo__section")
                count_line_total += 1

                count_line += 1

                # print(link, count_line)
                name_process = multiprocessing.current_process().name
                print('process--', name_process[-1:],':', count_line, '     total: ', count_line_total)

                if re.findall("индивидуальный предприниматель", str(contaner_html), flags=re.I):
                    await ip_data(contaner_html, link)
                if re.findall("Юридическое лицо", str(contaner_html), flags=re.I):
                    await ooo_data(contaner_html, link)
        except asyncio.exceptions.TimeoutError as exc:
            logger.warning(f"{link} -- {exc} asyncio.exceptions.TimeoutError")
        except aiohttp.ClientError as exc:
        # except Exception as exc:
            logger.warning(f"{link} -- {exc} aiohttp.ClientError")
        except aiohttp.ClientConnectorError as exc:
            await asyncio.sleep(15)
        except OSError as exc:
            logger.warning(f"{exc}")
        # except Exception as exc:
            logger.warning(f"{link} -- {exc} aiohttp.ClientConnectorError")


# async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):
#     # Getter function with semaphore.
#     async with semaphore:
#     # await asyncio.sleep(.5)
#         return await paths_ip_ooo(session, semaphore, link, auth, proxy_)

# ----тут async
async def create_tasks_soap(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN):
    contaner_links = get_links_by_segments(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN)

    for i in contaner_links:

        # print(links,'-=-=--')

        proxy_w = PROXY_IP
        proxy_auth = aiohttp.BasicAuth(PROXY_LOGIN, PROXY_PASS)

        rand_s = random.randint(18, 20)
        # rand_s = random.randint(6, 7)
        semaphore = asyncio.Semaphore(rand_s)
        rand_conn = random.randint(45, 55)
        # rand_conn = random.randint(19, 21)
        name_process = multiprocessing.current_process().name

        print(rand_conn, ' --conn |', rand_s, '--semaphore | ', count_links_total, '--links_total |', count_line_total, '--count_line_total |', 'process--', name_process[-1:])
        conn = aiohttp.TCPConnector(limit=rand_conn)


        async with aiohttp.ClientSession(connector=conn) as session:
        # async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(1200)) as session:
        # tasks = [interface_of_paths_ip_ooo(session, link, semaphore, auth=proxy_auth, proxy_="http://185.29.127.235:45785") for link in contaner_links]
            tasks = [interface_of_paths_ip_ooo(session, semaphore, link, auth=proxy_auth, proxy_=proxy_w) for link in
                     i]
            await asyncio.gather(*tasks)

        # try:
        #     response = requests.get(link, headers=headers)
        # ooo = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007263'
        # ip = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007265'
        #     soup = BeautifulSoup(response.text, "lxml")
        # check_company = soup.select_one()
        # yield soup
        # except ReadTimeout as exc:
        #     logger.error(f"{exc}")
        # except HTTPError as exc:
        #     logger.error(f"{exc}")
        # except ConnectionError as exc:
        #     logger.error(f"{exc}")
        #     time.sleep(15)

        # print(response.url)


async def ip_data(html, link):
    global count_total_new_email
    # title_ip = [
    #     'ФИО',
    #     'ИНН',
    #     'ОГРНИП',
    #     'Номер реестровой записи в ЕРУЗ',
    #     'Статус регистрации',
    #     'Дата регистрации в ЕИС',
    #     'Дата постановки на учет в налоговом органе',
    #     'Адрес электронной почты',
    # ]

    title_ip = {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": 'ФИО',
        "inn": 'ИНН',
        "ogrn": 'ОГРНИП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "email": 'Адрес электронной почты',
    }

    # keys_ip = [
    #     "full_name",
    #     "inn",
    #     "ogrn",
    #     "number_in_reestr",
    #     "status_registration_eis",
    #     "date_registration_eis",
    #     "date_registration_ifns",
    #     "email",
    # ]

    ip = {
        "number_in_reestr": None,
        "status_registration_eis": None,
        "date_registration_eis": None,
        "full_name": None,
        "inn": None,
        "ogrn": None,
        "date_registration_ifns": None,
        "email": None,
    }
    try:
        for key, value in title_ip.items():
            for record in html:
                soup = BeautifulSoup(record.text, "lxml")
                text = soup.select_one("html body p").get_text(strip=True)
                try:
                    title, data = text.strip().split('\n')
                except:
                    continue

                if value == title:
                    try:
                        if key == "full_name":
                            ip["full_name"] = data.upper()
                        elif key == "inn":
                            ip["inn"] = int(data)
                        elif key == "ogrn":
                            ip["ogrn"] = int(data)
                        elif key == "number_in_reestr":
                            ip["number_in_reestr"] = int(data)
                        elif key == "status_registration_eis":
                            ip["status_registration_eis"] = data
                        elif key == "date_registration_eis":
                            ip["date_registration_eis"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                        elif key == "date_registration_ifns":
                            ip["date_registration_ifns"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                        elif key == "email":
                            ip["email"] = data
                    except Exception as exc:
                        print(exc)
                        print('=======================================================')
        lid = Lids(
            category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
            date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
            inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
            status_registration_eis=ip["status_registration_eis"],
        )
        check_inn = session_base.query(Lids.inn).filter_by(inn=ip["inn"]).first()
        if not check_inn:
            session_base.add(lid)
            session_base.commit()
            count_total_new_email += 1
            print('---------------------------------------------------count_total_new_email -', count_total_new_email)
            logger.warning(f"count_total_new_email - {count_total_new_email}")

    except SQLAlchemyError as exc:
        session_base.rollback()


async def ooo_data(html, link):
    global count_total_new_email
    # print(html)
    # title_ooo = [
    #     'Номер реестровой записи в ЕРУЗ',
    #     'Статус регистрации',
    #     'Тип участника закупки',
    #     'Дата регистрации в ЕИС',
    #     'Полное наименование',
    #     'Сокращенное наименование',
    #     'Адрес в пределах места нахождения',
    #     'ИНН',
    #     'КПП',
    #     'Дата постановки на учет в налоговом органе',
    #     'ОГРН',
    #     'Адрес электронной почты',
    #     'Контактный телефон',
    # ]

    title_ooo = {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": "Полное наименование",
        "short_name": 'Сокращенное наименование',
        "address_yur": 'Адрес в пределах места нахождения',
        "inn": 'ИНН',
        "kpp": 'КПП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "ogrn": 'ОГРН',
        "email": 'Адрес электронной почты',
        "phone": 'Контактный телефон',
    }

    ooo = {
        "number_in_reestr": None,
        "status_registration_eis": None,
        "date_registration_eis": None,
        "full_name": None,
        "short_name": None,
        "address_yur": None,
        "inn": None,
        "kpp": None,
        "date_registration_ifns": None,
        "ogrn": None,
        "email": None,
        "phone": None,
    }
    try:
        for key, value in title_ooo.items():

            for record in html:
                soup = BeautifulSoup(record.text, "lxml")
                text = soup.select_one("html body p").get_text(strip=True)
                try:
                    title, data = text.strip().split('\n')
                except:
                    continue
                # except Exception as exc:
                #     logger.warning(f" {link} {exc} ---")
                if value == title:
                    if key == "full_name":
                        ooo["full_name"] = data.upper()
                    elif key == "short_name":
                        ooo["short_name"] = data
                    elif key == "address_yur":
                        ooo["address_yur"] = data
                    elif key == "inn":
                        ooo["inn"] = int(data)
                    elif key == "kpp":
                        ooo["kpp"] = int(data)
                    elif key == "ogrn":
                        ooo["ogrn"] = int(data)
                    elif key == "number_in_reestr":
                        ooo["number_in_reestr"] = int(data)
                    elif key == "status_registration_eis":
                        ooo["status_registration_eis"] = data
                    elif key == "date_registration_eis":
                        ooo["date_registration_eis"] = datetime.datetime.strptime(data.strip(), "%d.%m.%Y").date()
                    elif key == "date_registration_ifns":
                        ooo["date_registration_ifns"] = datetime.datetime.strptime(data.strip(), "%d.%m.%Y").date()
                    elif key == "email":
                        ooo["email"] = data
                    elif key == "phone":
                        ooo["phone"] = data
        lid = Lids(
            category_id=1, created_on=datetime.date.today(),
            date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
            short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
            ogrn=ooo["ogrn"], date_registration_eis=ooo["date_registration_eis"],
            status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
            kpp=ooo["kpp"], phone=ooo["phone"],
        )

        check_inn = session_base.query(Lids.inn).filter_by(inn=ooo["inn"]).first()
        if not check_inn:
            session_base.add(lid)
            session_base.commit()
            count_total_new_email += 1
            print('---------------------------------------------------count_total_new_email -', count_total_new_email)
            logger.warning(f"count_total_new_email - {count_total_new_email}")
    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")


    # print(start_segment_date)
    # print(end_segment_date)
    # period = str(period_pre.days)
    # print(period)


def main(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN):
    # logger.debug("Start!")

    start = time.time()
    # period_segment = 14
    #
    # start_date_str = '25.12.2018'
    # page = 1
    # per_page = 500
    print(period_segment, start_date_str, page, per_page, end_date)

    asyncio.run(create_tasks_soap(period_segment, start_date_str, page, per_page, end_date, PROXY_IP, PROXY_PASS, PROXY_LOGIN))
    print(time.time() - start)
    print(count_line_total)


if __name__ == "__main__":

    load_dotenv()
    PROXY_IP = os.getenv("PROXY_IP")
    PROXY_PASS = os.getenv("PROXY_PASS")
    PROXY_LOGIN = os.getenv("PROXY_LOGIN")

    start = time.time()
    period_segment = 14

    date_today_obj = datetime.datetime.today()
    date_today_str = datetime.datetime.strftime(date_today_obj, '%d.%m.%Y')

    default_start_date_obj = date_today_obj - datetime.timedelta(days=31)
    default_date_today_str = datetime.datetime.strftime(default_start_date_obj, '%d.%m.%Y')

    # user_start_date = os.environ.get('START_DATE', default_date_today_str)
    # start_date_1 = user_start_date
    # end_date_1 = '31.12.2018'
    start_date_1 = '31.12.2019'
    end_date_1 = date_today_str

    # start_date_2 = '25.12.2019'
    start_date_2 = '10.01.2020'
    end_date_2 = '31.12.2020'

    # start_date_3 = '25.12.2020'
    start_date_3 = '10.03.2022'
    end_date_3 = date_today_str

    page = 1
    per_page = 500

    import cleaner
    logger = logging.getLogger("proc_1")
    # logger = logging.getLogger("proc_2")
    # logger = logging.getLogger("proc_3")
    count_line_total = 0
    count_line = 0
    count_links_total = 0
    count_total_new_email = 0
    # try:
    #     main(period_segment, start_date_1, page, per_page, end_date_1)
    #     cleaner.main()
    # except Exception as exc:
    #     logger.exception('Common exception!', exc_info=exc)
    #     print('end')

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    try:
        proc_1 = pool.apply_async(main, [period_segment, start_date_1, page, per_page, end_date_1, PROXY_IP, PROXY_PASS, PROXY_LOGIN])
        # proc_2 = pool.apply_async(main, [period_segment, start_date_2, page, per_page, end_date_2])
        # proc_3 = pool.apply_async(main, [period_segment, start_date_3, page, per_page, end_date_3])
    except OSError as exc:
        logger.warning(f"{exc}")
    except Exception as exc:
        logger.warning(f"{exc} ----")

    pool.close()
    pool.join()

    print()
    cleaner.main()




