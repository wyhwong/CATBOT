import requests as req
from bs4 import BeautifulSoup
from overrides import overrides

from common_utils.logger import get_logger
from common_utils.common import load_yml
from .text_scraper import TextScraper, _get_keywords, _is_str


LOGGER = get_logger("text_analyzer/utils/news_scraper")


def _get_news_web_urls() -> dict:
    """
    Get news web urls.

    Args:
        None.
    Returns:
        News web urls (dict).
    """
    return load_yml("./configs/text_analyzer/web_urls.yml")


class NewsScraper(TextScraper):
    """
    News Scraper.
    """

    @overrides
    def __init__(self) -> None:
        """
        Initialize News Scraper.

        Args:
            None.
        Returns:
            None.
        """
        LOGGER.debug("Initializing News Scraper...")
        self.web_urls = _get_news_web_urls()
        self.keywords = _get_keywords()
        LOGGER.info("Initialized News Scraper.")

    @overrides
    def scrape(self, keywords: list = None) -> list:
        """
        Scrape news.

        Args:
            keywords (list): Keywords to filter the prompts.
        Returns:
            Prompts (list).
        """
        prompts = []
        for website, web_url in self.web_urls.items():
            LOGGER.info(f"Scraping {website}: {web_url}...")
            try:
                page = req.get(web_url)
                content = BeautifulSoup(page.content, "html.parser")
            except Exception as err:
                LOGGER.error(f"Encountered error: {err}")
                continue
            scraper_function = getattr(self, f"_scrape_{website}")
            prompts += scraper_function(content=content)
            LOGGER.debug(f"Got prompts: {prompts}.")

        if keywords:
            for prompt in reversed(prompts):
                keyword_in_prompt = False
                for keyword in keywords:
                    if keyword in prompt:
                        keyword_in_prompt = True
                if not keyword_in_prompt:
                    prompts.remove(prompt)
        return prompts

    @overrides
    def scrape_targets(self, targets: list) -> list:
        """
        Scrape news of the targets.

        Args:
            targets (list): Targets to filter the prompts.
        Returns:
            Prompts (list).
        """
        prompts = self.scrape(keywords=None)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)

    def _scrape_investing(self, content) -> list:
        """
        Scrape investing.com.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("a"):
            title = element.get("title")
            prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts

    def _scrape_tradingview(self, content) -> list:
        """
        Scrape tradingview.com.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("a"):
            try:
                title = element.div.find_all("span")[-1].contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts

    def _scrape_coindesk(self, content) -> list:
        """
        Scrape coindesk.com.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("a"):
            title = element.get("title")
            prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts

    def _scrape_decrypt(self, content) -> list:
        """
        Scrape decrypt.co.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("h4"):
            try:
                title = element.contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts

    def _scrape_coinmarketcap(self, content) -> list:
        """
        Scrape coinmarketcap.com.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("a"):
            try:
                title = element.contents[-1]
            except:
                title = None
            finally:
                prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts

    def _scrape_nytimes(self, content) -> list:
        """
        Scrape nytimes.com.

        Args:
            content (BeautifulSoup): Content of the web page.
        Returns:
            Prompts (list).
        """
        prompts = []
        for element in content.find_all("h2"):
            try:
                title = element.contents[-1].contents[-1]
            except:
                title = None
            prompts.append(title) if (title and _is_str(input=title)) else None
        return prompts
