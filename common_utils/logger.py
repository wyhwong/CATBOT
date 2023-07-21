import os
import logging

LOGLEVEL = int(os.getenv("LOGLEVEL", "20"))
LOGFMT = "%(asctime)s [%(name)s | %(levelname)s]: %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=LOGFMT, datefmt=DATEFMT, level=LOGLEVEL)


def get_logger(logger_name: str, log_filepath=None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOGLEVEL)
    if log_filepath:
        handler = logging.FileHandler(filename=log_filepath)
        formatter = logging.Formatter(fmt=LOGFMT, datefmt=DATEFMT)
        handler.setFormatter(fmt=formatter)
        logger.addHandler(handler)
    return logger
