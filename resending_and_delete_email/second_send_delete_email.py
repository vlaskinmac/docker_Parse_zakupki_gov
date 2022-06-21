import datetime

from pymongo import MongoClient

import logging.config

from logging_config import dict_config
from sender_mail import send_email


def second_send():

    """
        send_status:
            '1' - письмо отправлено 1 раз из 2
            '2' - письмо отправлено 2 раз из 2
            '200' - успешная отправка
            '404' - адрес не валиден
            '400' - общая ошибка при отправке письма
       """
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    # old_day = today - datetime.timedelta(days=1)
    # old_day_obj = sent_letters_collection.find(
    #     {"create_date": {"$gte": old_day, "$lte": yesterday}, "send_status": "1"}
    # )
    old_day_obj = sent_letters_collection.find(
        {"create_date": {"$gt": yesterday, "$lte": today}, "send_status": "1"}
    )
    count = 0
    for entire_id in old_day_obj:
        logger.debug(
            f"mongo вторая отправка письма:"
            f" email: {entire_id['email_address']},"
            f" инн: {entire_id['winner_inn']}"
            f" - {entire_id['tender_number']}\n"
        )
        send_status = send_email(entire_id)
        count += 1
        if send_status == "200":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "2"}})
        elif send_status == "404":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "404"}})
        elif send_status == "400":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "400"}})
        logger.debug(f"Количество повторных отправлений: {count}")


def delete_email():
    today = datetime.datetime.today()
    old_day_end = today - datetime.timedelta(days=5)
    old_day_start = today - datetime.timedelta(days=8)
    sent_letters_collection.delete_many(
        {"create_date": {"$gte": old_day_start, "$lt": old_day_end}, "send_status": "2"})


if __name__ == "__main__":
    logging.config.dictConfig(dict_config)
    logger = logging.getLogger('proc_1')
    # logging.disable(logging.DEBUG)
    # cluster = MongoClient("mongodb://localhost:27017")
    cluster = MongoClient("mongodb://194.67.92.2:27018")
    # mongo_url = os.environ.get('MONGO_URL')
    # cluster = MongoClient(mongo_url)
    sent_letters_db = cluster["sent_letter_db"]
    sent_letters_collection = sent_letters_db["sent_letters"]

    second_send()
    # delete_email()





