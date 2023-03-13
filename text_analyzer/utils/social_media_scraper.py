import praw
from overrides import overrides

from .news_scraper import TextScraper, _get_keywords
from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

LOGGER = get_logger(logger_name="Utils | Social Media Scraper")


def _get_subreddits():
    return read_content_from_yml(path="configs/subreddits.yml")


class RedditScraper(TextScraper):
    @overrides
    def __init__(self, client_id: str, client_secret: str, user_agent) -> None:
        self.reddit_client = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        self.keywords = _get_keywords()
        self.subreddits = _get_subreddits()

    @overrides
    def scrape(self, targets: list, hot_post_limit: int = 20) -> list:
        prompts = []
        for subreddit in self.subreddits:
            hot_posts = self.reddit_client.subreddit(subreddit).hot(limit=hot_post_limit)
            for post in hot_posts:
                prompts.append(post.title)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)
