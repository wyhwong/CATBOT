import requests as req
from bs4 import BeautifulSoup
from overrides import overrides

from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml
from .text_scraper import TextScraper, _get_keywords


LOGGER = get_logger(logger_name="Utils | News Scraper")


def _get_news_web_urls() -> dict:
    return read_content_from_yml(path="./configs/web_urls.yml")


class NewsScraper(TextScraper):
    @overrides
    def __init__(self) -> None:
        self.web_urls = _get_news_web_urls()
        self.keywords = _get_keywords()

    @overrides
    def scrape(self, targets: list) -> list:
        prompts = []
        for website, web_url in self.web_urls.items():
            page = req.get(web_url)
            content = BeautifulSoup(page.content, "html.parser")
            prompts += getattr(self, f"_scrape_{website}")(content=content)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)

    def _scrape_investing(content) -> list:
        prompts = []
        for element in content.find_all("a"):
            title = element.get("title")
            prompts.append(title) if title else None
        return prompts

    def _scrape_tradingview(content) -> list:
        prompts = []
        for element in content.find_all("a"):
            try:
                title = element.div.find_all("span")[-1].contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if title else None
        return prompts

    def _scrape_coindesk(content) -> list:
        prompts = []
        for element in content.find_all("a"):
            title = element.get("title")
            prompts.append(title) if title else None
        return prompts

    def _scrape_decrypt(content) -> list:
        prompts = []
        for element in content.find_all("h4"):
            try:
                title = element.contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if title else None
        return prompts

    def _scrape_coinmarketcap(content) -> list:
        prompts = []
        for element in content.find_all("a"):
            try:
                title = element.contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if title else None
        return prompts

    def _scrape_nytimes(content) -> list:
        prompts = []
        for element in content.find_all("h2"):
            try:
                title = element.contents[-1].contents[-1]
            except:
                title = None
            prompts.append(title) if title else None
        return prompts
