from overrides import overrides

from .news_scraper import TextScraper, _get_keywords
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Social Media Scraper")


class SocialMediaScraper(TextScraper):
    @overrides
    def __init__(self) -> None:
        self.keywords = _get_keywords()

    @overrides
    def scrape(self, targets: list) -> list:
        pass
