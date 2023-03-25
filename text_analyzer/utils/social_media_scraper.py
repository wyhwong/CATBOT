import praw
import tweepy
from overrides import overrides

from .news_scraper import TextScraper, _get_keywords, _is_str
from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

LOGGER = get_logger(logger_name="Utils | Social Media Scraper")


def _get_subreddits():
    return read_content_from_yml(path="configs/text_analyzer/subreddits.yml")


class RedditScraper(TextScraper):
    @overrides
    def __init__(self, client_id: str, client_secret: str, user_agent) -> None:
        LOGGER.info("Initializing Reddit Scraper...")
        self.reddit_client = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        self.keywords = _get_keywords()
        self.subreddits = _get_subreddits()
        LOGGER.info("Initialized Reddit Scraper.")

    @overrides
    def scrape(self, keywords: list = None, hot_post_limit: int = 50) -> list:
        prompts = []
        try:
            for subreddit in self.subreddits:
                hot_posts = self.reddit_client.subreddit(subreddit).hot(limit=hot_post_limit)
                for post in hot_posts:
                    if post.title and _is_str(input=post.title):
                        prompts.append(post.title)
        except Exception as err:
            LOGGER.error(f"Encountered error: {err}")
            return prompts

        if keywords:
            for prompt in reversed(prompts):
                for keyword in keywords:
                    if keyword not in prompt:
                        prompts.remove(prompt)
        return prompts

    @overrides
    def scrape_targets(self, targets: list, hot_post_limit: int = 50) -> list:
        prompts = self.scrape(keywords=None, hot_post_limit=hot_post_limit)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)


class TwitterScraper(TextScraper):
    @overrides
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str) -> None:
        LOGGER.info("Initializing Twitter Scraper.")
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
        self.keywords = _get_keywords()
        LOGGER.info("Initialized Twitter Scraper.")

    @overrides
    def scrape(self, keywords, post_limit: int = 20) -> list:
        prompts = []
        try:
            tweets = self.twitter.search_tweets(q=keywords, count=post_limit)
            for tweet in tweets:
                if tweet.text and _is_str(input=tweet.text):
                    prompts.append(tweet.text)
                # TODO: Use favourite count to weight the tweets
                # tweet.favorite_count
        except Exception as err:
            LOGGER.error(f"Encountered error: {err}")
            return prompts
        return prompts

    @overrides
    def scrape_targets(self, targets: list, post_limit: int = 20) -> list:
        prompts = []
        for target in targets:
            prompts += self.scrape(keywords=self.keywords[target], post_limit=post_limit)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)
