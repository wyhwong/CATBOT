from abc import ABC, abstractmethod
from p_tqdm import p_map, t_imap

from common_utils.common import read_content_from_yml


def _get_keywords() -> dict:
    return read_content_from_yml(path="./configs/keywords.yml")


def _does_prompt_contain_keywords(keywords: list, prompt: str) -> str:
    for keyword in keywords:
        if keyword in prompt:
            return prompt


def _dummy_function(any_input: any) -> any:
    return any_input


class TextScraper(ABC):
    @abstractmethod
    def __init__(self):
        self.keywords = _get_keywords()

    @abstractmethod
    def scrape(self, targets: list) -> list:
        pass

    def _filter_prompts_with_keywords(self, targets: list, prompts: list):
        target_prompts = dict.fromkeys(targets, [])
        for target in targets:
            keywords = t_imap(_dummy_function, self.keywords[target] * len(prompts))
            prompts_with_keywords = p_map(_does_prompt_contain_keywords, keywords, prompts)
            target_prompts[target] = list(filter(None, prompts_with_keywords))
        return target_prompts
