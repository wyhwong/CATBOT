import requests as req
from bs4 import BeautifulSoup
from p_tqdm import p_map, t_imap

from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

LOGGER = get_logger(logger_name="Utils | Text Scraper")


def _get_web_urls():
    return read_content_from_yml(path="./configs/web_urls.yml")


def _get_keywords():
    return read_content_from_yml(path="./configs/keywords.yml")


def _does_prompt_contain_keywords(keywords, prompt):
    for keyword in keywords:
        if keyword in prompt:
            return prompt


def _dummy_function(any_input):
    return any_input


class TextScraper:
    def __init__(self) -> None:
        self.web_urls = _get_web_urls()
        self.keywords = _get_keywords()

    def scrap(self, targets):
        target_prompts = dict.fromkeys(targets, [])
        prompts = []
        for website, web_url in self.web_urls.items():
            page = req.get(web_url)
            content = BeautifulSoup(page.content, "html.parser")
            prompts += getattr(self, f"_scrap_{website}")(content=content)

        for target in targets:
            keywords = t_imap(_dummy_function, self.keywords[target] * len(prompts))
            prompts_with_keywords = p_map(_does_prompt_contain_keywords, keywords, prompts)
            target_prompts[target] = list(filter(None, prompts_with_keywords))
        return target_prompts

    def _scrap_investing(content) -> list:
        prompts = []
        for element in content.find_all("a"):
            title = element.get("title")
            prompts.append(title) if title else None
        return prompts

    def _scrap_tradingview(content) -> list:
        prompts = []
        return prompts

    def _scrap_bloomberg(content) -> list:
        prompts = []
        return prompts

    def _scrap_coindesk(content) -> list:
        prompts = []
        return prompts

    def _scrap_decrypt(content) -> list:
        prompts = []
        return prompts

    def _scrap_decrypt(content) -> list:
        prompts = []
        return prompts

    def _scrap_coinmarketcap(content) -> list:
        prompts = []
        return prompts
