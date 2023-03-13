import requests as req
from bs4 import BeautifulSoup
from p_tqdm import p_map, t_imap
from overrides import overrides

from common_utils.logger import get_logger
from .text_scraper import TextScraper, _does_prompt_contain_keywords, _dummy_function, _get_keywords, _get_news_web_urls


LOGGER = get_logger(logger_name="Utils | News Scraper")


class NewsScraper(TextScraper):
    @overrides
    def __init__(self) -> None:
        self.web_urls = _get_news_web_urls()
        self.keywords = _get_keywords()

    @overrides
    def scrape(self, targets: list) -> list:
        target_prompts = dict.fromkeys(targets, [])
        prompts = []
        for website, web_url in self.web_urls.items():
            page = req.get(web_url)
            content = BeautifulSoup(page.content, "html.parser")
            prompts += getattr(self, f"_scrape_{website}")(content=content)

        for target in targets:
            keywords = t_imap(_dummy_function, self.keywords[target] * len(prompts))
            prompts_with_keywords = p_map(_does_prompt_contain_keywords, keywords, prompts)
            target_prompts[target] = list(filter(None, prompts_with_keywords))
        return target_prompts

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
