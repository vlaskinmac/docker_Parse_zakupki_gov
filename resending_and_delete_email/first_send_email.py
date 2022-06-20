import datetime

from pymongo import MongoClient

import logging.config

from logging_config import dict_config
from sender_mail import send_email


def first_send():
    """
        send_status:
            '1' - письмо отправлено 1 раз из 2
            '200' - успешная отправка
            '404' - адрес не валиден
            '400' - общая ошибка при отправке письма
       """

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_obj = sent_letters_collection.find(
        {"create_date": {"$gt": yesterday, "$lte": today}, "send_status": None}
    )

    for entire_id in yesterday_obj:
        logger.debug(
            f"mongo первая отправка письма:"
            f" email: {entire_id['email_address']},"
            f" инн: {entire_id['winner_inn']}\n"
        )
        send_status = send_email(entire_id)
        if send_status == "200":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "1"}})
        elif send_status == "404":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "404"}})
        elif send_status == "400":
            sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"send_status": "400"}})


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

    first_send()


