import asyncio
import logging.config
import datetime
import os
import random
import shlex
import subprocess
import time
import re
import aiofiles
import aiohttp

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from logging_config import dict_config
from orm_models import Lids

postgres_url = os.environ.get('ENGINE')
engine = create_engine(postgres_url)

# engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session_base = Session()

logging.config.dictConfig(dict_config)
logger = logging.getLogger("proc_2")

count_line = 0


async def headers_random():
    async with aiofiles.open("headers", 'r') as file:
        headers_list = await file.read()
        headers = str(headers_list).split('\n')

    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head


async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):
    global count_line
    await asyncio.sleep(random.randint(0, 1))
    async with semaphore:
        head = await headers_random()
        try:
            await asyncio.sleep(random.randint(4, 7))
            async with session.get(url=link, proxy_auth=auth, ssl=False, proxy=proxy_, headers=head) as response:
                soup = BeautifulSoup(await response.text(), "lxml")

                contaner_html = soup.select(".blockInfo__section")

                count_line += 1

                print(count_line)

                if re.findall("индивидуальный предприниматель", str(contaner_html), flags=re.I):
                    await ip_data(contaner_html, link)
                if re.findall("Юридическое лицо", str(contaner_html), flags=re.I):
                    await ooo_data(contaner_html, link)
        except asyncio.exceptions.TimeoutError as exc:
            logger.warning(f"{link} -- {exc} asyncio.exceptions.TimeoutError")
        except aiohttp.ClientError as exc:

            logger.warning(f"{link} -- {exc} aiohttp.ClientError")
        except aiohttp.ClientConnectorError as exc:
            await asyncio.sleep(15)

            logger.warning(f"{link} -- {exc} aiohttp.ClientConnectorError")


# ----тут async
async def create_tasks_soap():
    load_dotenv()
    PROXY_IP = os.getenv("PROXY_IP")
    PROXY_PASS = os.getenv("PROXY_PASS")
    PROXY_LOGIN = os.getenv("PROXY_LOGIN")
    contaner_links = []

    async with aiofiles.open("logfile_links.txt") as file:
        contaner = await file.read()
        contaner_links_pre = str(contaner).strip().split('\n')

        for link in contaner_links_pre:
            if re.search(r"https", str(link)):
                contaner_links.append(link)
        #         print(link)
        #     breakpoint()
        #     breakpoint()
        # breakpoint()
        print(len(contaner_links))

    proxy_w = PROXY_IP
    proxy_auth = aiohttp.BasicAuth(PROXY_LOGIN, PROXY_PASS)

    rand_s = random.randint(18, 20)
    semaphore = asyncio.Semaphore(rand_s)
    rand_conn = random.randint(60, 70)

    print(rand_conn, ' --conn |', rand_s, '--semaphore ')
    conn = aiohttp.TCPConnector(limit=rand_conn)

    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [interface_of_paths_ip_ooo(session, semaphore, link, auth=proxy_auth, proxy_=proxy_w) for link in
                 contaner_links]
        await asyncio.gather(*tasks)


async def ip_data(html, link):

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
    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")


async def ooo_data(html, link):

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
            ogrn=ooo["ogrn"], date_registration_eis =ooo["date_registration_eis"],
            status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
            kpp=ooo["kpp"], phone=ooo["phone"],
        )
        check_inn = session_base.query(Lids.inn).filter_by(inn=ooo["inn"]).first()
        if not check_inn:
            session_base.add(lid)
            session_base.commit()
    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")


def main():
    get_links_from_logfiles()
    logger.warning("--- Start probe!--- ")

    start = time.time()

    asyncio.run(create_tasks_soap())

    print(time.time() - start)
    print('end============================================================')


def get_links_from_logfiles():
    """ Получает ссылки  из лог файла для повторной обработки """

    file_name = os.path.abspath('logfile_1.txt')
    command_str = f"awk '{{print $14}}' {file_name}"
    comman = shlex.split(command_str)
    popen = subprocess.Popen(comman, stdout=subprocess.PIPE, universal_newlines=True)
    std = popen.stdout.read().strip()
    memory = std.split('\n')

    with open('logfile_links.txt', 'a') as file:
        for i in memory:
            if i:
                file.write(i + '\n')
    # os.remove(file_name)


if __name__ == "__main__":
    count_line = 0
    try:
        main()
    except Exception as exc:
        logger.exception('Common exception!', exc_info=exc)
        print('end')







