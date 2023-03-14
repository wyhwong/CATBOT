import praw
import tweepy
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


class TwitterScraper(TextScraper):
    @overrides
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str) -> None:
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
        self.keywords = _get_keywords()

    @overrides
    def scrape(self, targets: list, post_limit: int = 20) -> list:
        prompts = []
        for target in targets:
            tweets = self.twitter.search_tweets(q=self.keywords[target], count=post_limit)
            for tweet in tweets:
                prompts.append(tweet.text)
                # TODO: Use favourite count to weight the tweets
                # tweet.favorite_count
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)
