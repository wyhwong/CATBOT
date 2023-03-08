import requests as req
from bs4 import BeautifulSoup

from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

LOGGER = get_logger(logger_name="Utils | Text Scraper")


def _get_web_urls():
    return read_content_from_yml(path="./configs/web_urls.yml")


class TextScraper:
    def __init__(self) -> None:
        self.web_urls = _get_web_urls()

    def __call__(self, targets):
        target_prompts = dict.fromkeys(targets, [])
        for website, web_url in self.web_urls.items():
            page = req.get(web_url)
            content = BeautifulSoup(page.content, "html.parser")
            prompts = getattr(self, f"_scrap_{website}")(content=content)
            for prompt in prompts:
                for target in targets:
                    target_prompts[target].append(prompt) if (target in prompt) else None
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
