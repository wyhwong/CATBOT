import praw
import tweepy
from overrides import overrides

from .news_scraper import TextScraper, _get_keywords, _is_str
from common_utils.logger import get_logger
from common_utils.common import load_yml

LOGGER = get_logger("text_analyzer/utils/social_media_scraper")


def _get_subreddits():
    """
    Get subreddits.

    Args:
        None.
    Returns:
        Subreddits (list).
    """
    return load_yml("configs/text_analyzer/subreddits.yml")


class RedditScraper(TextScraper):
    """
    Reddit Scraper.
    """

    @overrides
    def __init__(self, client_id: str, client_secret: str, user_agent) -> None:
        """
        Initialize Reddit Scraper.

        Args:
            client_id (str): Client ID.
            client_secret (str): Client secret.
            user_agent (str): User agent.
        Returns:
            None.
        """
        LOGGER.debug("Initializing Reddit Scraper...")
        self.reddit_client = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )
        self.keywords = _get_keywords()
        self.subreddits = _get_subreddits()
        LOGGER.info("Initialized Reddit Scraper.")

    @overrides
    def scrape(self, keywords: list = None, hot_post_limit: int = 50) -> list:
        """
        Scrape Reddit.

        Args:
            keywords (list): Keywords to filter the prompts.
            hot_post_limit (int): Limit of hot posts to scrape.
        Returns:
            Prompts (list).
        """
        prompts = []
        try:
            for subreddit in self.subreddits:
                hot_posts = self.reddit_client.subreddit(subreddit).hot(
                    limit=hot_post_limit
                )
                for post in hot_posts:
                    if post.title and _is_str(input=post.title):
                        prompts.append(post.title)
        except Exception as err:
            LOGGER.error(f"Encountered error: {err}")
            return prompts

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
    def scrape_targets(self, targets: list, hot_post_limit: int = 50) -> list:
        """
        Scrape Reddit with targets.

        Args:
            targets (list): Targets to filter the prompts.
            hot_post_limit (int): Limit of hot posts to scrape.
        Returns:
            Prompts (list).
        """
        prompts = self.scrape(keywords=None, hot_post_limit=hot_post_limit)
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)


class TwitterScraper(TextScraper):
    """
    Twitter Scraper.
    """

    @overrides
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str,
    ) -> None:
        """
        Initialize Twitter Scraper.

        Args:
            consumer_key (str): Consumer key.
            consumer_secret (str): Consumer secret.
            access_token (str): Access token.
            access_token_secret (str): Access token secret.
        Returns:
            None.
        """
        LOGGER.debug("Initializing Twitter Scraper.")
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
        self.keywords = _get_keywords()
        LOGGER.info("Initialized Twitter Scraper.")

    @overrides
    def scrape(self, keywords, post_limit: int = 20) -> list:
        """
        Scrape Twitter.

        Args:
            keywords (list): Keywords to filter the prompts.
            post_limit (int): Limit of posts to scrape.
        Returns:
            Prompts (list).
        """
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
        """
        Scrape Twitter with targets.

        Args:
            targets (list): Targets to filter the prompts.
            post_limit (int): Limit of posts to scrape.
        Returns:
            Prompts (list).
        """
        prompts = []
        for target in targets:
            prompts += self.scrape(
                keywords=self.keywords[target], post_limit=post_limit
            )
        return self._filter_prompts_with_keywords(targets=targets, prompts=prompts)
