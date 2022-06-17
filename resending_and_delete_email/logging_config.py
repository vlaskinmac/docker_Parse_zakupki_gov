

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(levelname)s | logger-%(name)s | %(asctime)s | %(filename)s | %(funcName)s() | line-%(lineno)d | %(message)s | %(processName)s"
        },
        "except": {
            "format": "%(levelname)s | logger-%(name)s | %(asctime)s | %(filename)s | %(message)s | %(processName)s"
        },
    },
    "handlers": {
        "console_1": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            # "level": "WARNING",
            "formatter": "base"
        },
        "file_1": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "base",
            "filename": "logfile_1.txt",
            "mode": "a"
        },
        "console_except": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            # "level": "WARNING",
            "formatter": "except"
        },
        "file_except": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "except",
            "filename": "logfile_except.txt",
            "mode": "a"
        },
        "console_3": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            # "level": "WARNING",
            "formatter": "base"
        },
        "file_3": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "base",
            "filename": "logfile_crud.txt",
            "mode": "a"
        },
    },
    "loggers": {
        "proc_1": {
            "level": "DEBUG",
            "handlers": ["file_1", "console_1"],
            # "propagate": False,
        },
        "except": {
            "level": "DEBUG",
            "handlers": ["file_except", "console_except"],
            # "propagate": True,
        },
        "crud": {
            "level": "DEBUG",
            "handlers": ["file_3", "console_3"],
            # "propagate": False,
        }
    },

    # "filters": {},
    # "root": {} # == "": {}
}

