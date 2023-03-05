import yaml
import os

from .logger import get_logger

LOGGER = get_logger("Common Utils | Common")

def read_content_from_yml(path:str) -> dict:
    LOGGER.info(f"Reading {path}...")
    with open(path, "r") as file:
        content = yaml.load(file, Loader=yaml.SafeLoader)
    LOGGER.debug(f"Content: {content}.")
    return content


def save_dict_as_yml(path:str, input_dict:dict) -> None:
    LOGGER.debug(f"Saving dict: {input_dict}...")
    with open(path, 'w') as file:
        yaml.dump(input_dict, file)
    LOGGER.info(f"Saved dictionary at {path}.")


def check_and_create_dir(directory:str) -> bool:
    exist = os.path.isdir(directory)
    LOGGER.debug(f"{directory} exists: {exist}")
    if not exist:
        LOGGER.info(f"{directory} does not exist, creating one.")
        os.mkdir(directory)
    return exist