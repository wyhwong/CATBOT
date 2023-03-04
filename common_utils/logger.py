import os
import logging


def get_logger(logger_name: str, log_file_path=None) -> logging.Logger:
    format = "%(asctime)s [%(name)s | %(levelname)s]: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logger = logging.getLogger(logger_name)
    level = os.getenv("LOGLEVEL")
    if level is None:
        logger.info(f"GetEnvError or running in local environment.")
        level = 20
    else:
        level = int(level)
    if log_file_path:
        handlers = [logging.FileHandler(log_file_path), logging.StreamHandler()]
    else:
        handlers = [logging.StreamHandler()]
    logging.basicConfig(level=level, format=format, datefmt=datefmt, handlers=handlers, force=True)
    logger.debug(f"Logger started, level={level}")
    return logger
