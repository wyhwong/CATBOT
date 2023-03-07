import os
import logging

FORMAT = "%(asctime)s [%(name)s | %(levelname)s]: %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=FORMAT, datefmt=DATEFMT)


def get_logger(logger_name: str, log_file_path=None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    level = os.getenv("LOGLEVEL")
    if level is None:
        logger.info(f"GetEnvError or running in local environment.")
        level = 20
    else:
        level = int(level)
    logger.setLevel(level=level)
    logger.addHandler(logging.StreamHandler())
    if log_file_path:
        logger.addHandler(logging.FileHandler(log_file_path))
    logger.debug(f"Logger started, level={level}")
    return logger
