import os
import logging


def getLogger(logger_name:str, logfilePath=None) -> logging.Logger:
    format = "%(asctime)s [%(name)s | %(levelname)s]: %(message)s"
    datefmt = '%Y-%m-%d %H:%M:%S'
    logger = logging.getLogger(logger_name)
    level = os.getenv("LOGLEVEL")
    if level is None:
        logger.info(f"GetEnvError or running in local environment.")
        level = 20
    else:
        level = int(level)
    if logfilePath:
        handlers = [logging.FileHandler(logfilePath), logging.StreamHandler()]
    else:
        handlers = [logging.StreamHandler()]
    logging.basicConfig(level=level,
                        format=format,
                        datefmt=datefmt,
                        handlers=handlers,
                        force=True)
    logger.debug(f"Logger started, level={level}")
    return logger
