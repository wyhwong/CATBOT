import yaml
import os

from .logger import get_logger

LOGGER = get_logger("common_utils/common")


def load_yml(filepath: str) -> dict:
    LOGGER.debug(f"Read yml: {filepath}")
    with open(filepath, "r") as file:
        yml_content = yaml.load(file, Loader=yaml.SafeLoader)
    return yml_content


def save_dict_as_yml(filepath: str, input_dict: dict) -> None:
    with open(filepath, "w") as file:
        yaml.dump(input_dict, file)
    LOGGER.info(f"Saved config at {filepath}")


def check_and_create_dir(dirpath: str) -> bool:
    exist = os.path.isdir(dirpath)
    LOGGER.debug(f"{dirpath} exists: {exist}")
    if not exist:
        LOGGER.info(f"{dirpath} does not exist, creating one.")
        os.mkdir(dirpath)
    return exist
