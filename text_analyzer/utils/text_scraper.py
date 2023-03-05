from bs4 import BeautifulSoup
import requests as req

from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

LOGGER = get_logger(logger_name="Utils | Text Scraper")


def _get_web_urls():
    return read_content_from_yml(path="./configs/web_urls.yml")


class TextScraper:
    def __init__(self) -> None:
        self.web_urls = _get_web_urls()["web_urls"]

    def __call__(self, targets):
        scraped_text = []
        for web_url in self.web_urls:
            page = req.get(web_url)
            content = BeautifulSoup(page.content, "html.parser")
            for idx, link in enumerate(content.find_all('a')):
                if(str(type(link.string)) == "<class 'bs4.element.NavigableString'>" and len(link.string) > 35):
                    print(str(idx)+".", link.string)
