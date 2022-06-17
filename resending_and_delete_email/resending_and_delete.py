import datetime
import os
import time

from pymongo import MongoClient

import logging.config
from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('proc_1')
# logging.disable(logging.DEBUG)


# from resender_mail import send_email

if __name__ == "__main__":
    # cluster = MongoClient("mongodb://localhost:27017")
    mongo_url = os.environ.get('MONGO_URL')
    cluster = MongoClient(mongo_url)

    sent_letters_db = cluster["sent_letter_db"]
    sent_letters_collection = sent_letters_db["sent_letters"]
    today = datetime.date.today()


    def resending_email():
        run_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=10,
            minute=1
        )
        start = run_date - datetime.timedelta(minutes=1)
        end = run_date + datetime.timedelta(minutes=1)
        logger.debug(f"mongo время старта повторной отправки письма:{start}")

        if start < run_date < end:
            yesterday = today - datetime.timedelta(days=1)
            yesterday_obj = sent_letters_collection.find({"create_date": yesterday})
            for entire_id in yesterday_obj:
                logger.debug(
                    f"mongo повторная отправка письма:"
                    f" вчерашняя дата: {entire_id['create_date']},"
                    f" email: {entire_id['email_address']},"
                    f" инн: {entire_id['winner_inn']}\n"
                )
                # повторная отправка письма
                # send_email(entire_id)
                sent_letters_collection.update_one({"_id": entire_id["_id"]}, {"$set": {"flag_resending_and_delete_email": 2}})
            time.sleep(60)

    def delete_email():
        run_date = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=16,
            minute=1
        )
        start = run_date - datetime.timedelta(minutes=1)
        end = run_date + datetime.timedelta(minutes=1)

        if start < run_date < end:
            four_days_ago = today - datetime.timedelta(days=6)

            delete_obj = sent_letters_collection.find({"create_date": four_days_ago})
            logger.debug(
                f"mongo удаление записи с датой ранее 4-дней:"
                f" вчерашняя дата: {delete_obj},\n"
            )

            sent_letters_collection.delete_many({"create_date": four_days_ago})
            time.sleep(60)



