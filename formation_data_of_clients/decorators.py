import time
from socket import socket

import urllib3
from requests import ReadTimeout, HTTPError, ConnectTimeout, Timeout
from functools import wraps

import logging.config

from requests.exceptions import ProxyError, SSLError
from urllib3.exceptions import ReadTimeoutError, PoolError

from logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('except')


def requests_exception(func):
    @wraps(func)
    def decorated_exception(*args, **kwargs):
        try:
            try:
                try:
                    return func(*args, **kwargs)
                except ReadTimeout as exc:
                    logger.warning(f'ReadTimeout - {exc}')
                except ConnectTimeout as exc:
                    logger.warning(f'ConnectTimeout - {exc}')
                except ProxyError as exc:
                    logger.warning(f'ProxyError - {exc}')
                except SSLError as exc:
                    logger.warning(f'SSLError - {exc}')
                except Timeout as exc:
                    logger.warning(f'Timeout - {exc}')
                except HTTPError as exc:
                    logger.warning(f'HTTPError - {exc}')
                except socket.timeout as exc:
                    logger.warning(f'socket.timeout sleep 15 sec.- {exc}')
                    time.sleep(15)
                except ConnectionError as exc:
                    logger.warning(f'ConnectionError sleep 15 sec. -  {exc}')
                    time.sleep(15)
                except urllib3.exceptions.MaxRetryError as exc:
                    time.sleep(15)
                    logger.warning(f'MaxRetryError sleep 15 sec. -  {exc}')
                except OSError as exc:
                    logger.warning(f'OSError - {exc}')
                except ReadTimeoutError as exc:
                    logger.warning(f'{func.__name__}() | ReadTimeoutError: - {exc} ')
                except PoolError as exc:
                    logger.warning(f'{func.__name__}() | PoolError: - {exc} ')
                except Exception as exc:
                    logger.warning(f'{func.__name__}() | Common Exception: - {exc} ')

        # except EOFError as exc:
        #     print(exc)
        # except ReadTimeoutError as exc:
        #     print(exc)
        # except ReadTimeout as exc:
        #     print(exc)
        # except socket.timeout as exc:
        #     print(exc)
            except Exception as exc:
                logger.warning(f'{func.__name__}() | Common - 2 Exception: - {exc} ')
        except Exception as exc:
            logger.warning(f'{func.__name__}() | Common - 3 Exception: - {exc} ')
    return decorated_exception


def common_exception(func):
    @wraps(func)
    def decorated_exception(*args, **kwargs):
        # try:
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            logger.warning(f'ValueError - {exc}')
        except IndexError as exc:
            logger.warning(f'PIndexError - {exc}')
        except NameError as exc:
            logger.warning(f'{func.__name__}() | NameError: - {exc} ')
        except AttributeError as exc:
            logger.warning(f'AttributeError - {exc}')
        except TypeError as exc:
            logger.warning(f'TypeError - {exc}')
        except BlockingIOError as exc:
            logger.warning(f'BlockingIOError - {exc}')
        except ChildProcessError as exc:
            logger.warning(f'ChildProcessError - {exc}')
        except KeyError as exc:
            logger.warning(f'KeyError -  {exc}')
            time.sleep(5)
        except EOFError as exc:
            logger.warning(f'{func.__name__}() | EOFError - {exc} ')
        except OSError as exc:
            logger.warning(f'OSError - {exc}')
        except Exception as exc:
            logger.warning(f'{func.__name__}() | Common Exception: - {exc} ')
        # except Exception as exc:
        #     logger.warning(f'{func.__name__}() | Common - 2 Exception: - {exc} ')

    return decorated_exception


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()
        result = func(*args, **kwargs)
        ended_at = time.time()
        elapsed = round(ended_at - started_at, 6)
        print(f'Функция {func.__name__} работала {elapsed} секунд(ы)')
        return result

    return surrogate




