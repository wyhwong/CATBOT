from abc import ABC, abstractmethod
from common_utils.common import read_content_from_yml


def _get_news_web_urls() -> dict:
    return read_content_from_yml(path="./configs/web_urls.yml")


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
    def __init__():
        pass

    @abstractmethod
    def scrape():
        pass
