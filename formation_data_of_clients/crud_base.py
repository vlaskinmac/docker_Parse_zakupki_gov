import logging.config
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from logging_config import dict_config

logging.config.dictConfig(dict_config)

# logging.disable(logging.DEBUG)


logger = logging.getLogger("crud")

# engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")

postgres_url = os.environ.get('ENGINE')
engine = create_engine(postgres_url)

Session = sessionmaker(bind=engine)
session_base = Session()

# inn = '366235585940'
# inn = '7724432801'


def get_email(inn):
    try:
        email = session_base.execute("select email from lids where inn=%s" % inn).fetchall()
        full_name = session_base.execute("select full_name from lids where inn=%s" % inn).fetchall()
        short_name = session_base.execute("select short_name from lids where inn=%s" % inn).fetchall()
        phone = session_base.execute("select phone from lids where inn=%s" % inn).fetchall()
        # print(str(*email.first()))
        # return email[0][0]
        # full_name = full_name[0][0]
        # short_name = short_name[0][0]
        # phone = phone[0][0]
        # email = email[0][0]
        return full_name[0][0], short_name[0][0], phone[0][0], email[0][0]
    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{'link'} {exc} -- rollback - SQLAlchemyError")
    except TypeError:
        pass

# get_email(inn)