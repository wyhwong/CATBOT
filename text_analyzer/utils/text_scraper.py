import numpy as np
from abc import ABC, abstractmethod
from p_tqdm import p_map, t_imap

from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Text Scaper")


def _get_keywords() -> dict:
    return read_content_from_yml(path="./configs/keywords.yml")


def _does_prompt_contain_keywords(prompt: str, keywords: list) -> str:
    for keyword in keywords:
        if keyword.lower() in prompt.lower():
            return prompt


def _is_str(input) -> bool:
    if type(input) != str:
        return False
    return True


def _dummy_function(any_input: any) -> any:
    return any_input


class TextScraper(ABC):
    @abstractmethod
    def __init__(self):
        self.keywords = _get_keywords()

    @abstractmethod
    def scrape(self, keywords: list) -> list:
        pass

    @abstractmethod
    def scrape_targets(self, targets: list) -> list:
        pass

    def _filter_prompts_with_keywords(self, targets: list, prompts: list):
        target_prompts = dict.fromkeys(targets, [])
        if not prompts:
            return target_prompts
        for target in targets:
            keywords = t_imap(_dummy_function, [self.keywords[target]] * len(prompts))
            prompts_with_keywords = p_map(
                _does_prompt_contain_keywords, np.array(prompts, dtype=str), keywords
            )
            target_prompts[target] = list(filter(None, prompts_with_keywords))
        return target_prompts
