#!/usr/bin/env python3
import os

from utils.handler import Handler
from utils.news_scraper import NewsScraper
from utils.social_media_scraper import RedditScraper, TwitterScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker

LOGGER = get_logger("Text Analyzer")


def main() -> None:
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
    if reddit_client_id and reddit_client_secret and reddit_user_agent:
        reddit_scraper = RedditScraper(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent,
        )
    else:
        reddit_scraper = None

    tweepy_consumer_key = os.getenv("TWEEPY_CONSUMER_KEY")
    tweepy_consumer_secret = os.getenv("TWEEPY_CONSUMER_SECRET")
    tweepy_access_token = os.getenv("TWEEPY_ACCESS_TOKEN")
    tweepy_access_token_secret = os.getenv("TWEEPY_ACCESS_TOKEN_SECRET")
    if tweepy_consumer_key and tweepy_consumer_secret and tweepy_access_token and tweepy_access_token_secret:
        twitter_scraper = TwitterScraper(
            consumer_key=tweepy_consumer_key,
            consumer_secret=tweepy_consumer_secret,
            access_token=tweepy_access_token_secret,
            access_token_secret=tweepy_access_token_secret,
        )
    else:
        twitter_scraper = None

    text_scraper = NewsScraper()
    text_inference = ClassificationInference(pretrained=os.getenv("TEXT_INFERENCE_PRETRAINED"))
    publisher = Publisher(client_id="text-analyzer-pub", broker=Broker())
    handler = Handler(
        text_inference=text_inference,
        news_scraper=text_scraper,
        reddit_scraper=reddit_scraper,
        twitter_scraper=twitter_scraper,
        publisher=publisher,
    )
    subscriber = Subscriber(client_id="text-analyzer-sub", broker=Broker(), topic="slackbot-pub", handlers=[handler])
    subscriber.start()


if __name__ == "__main__":
    main()
