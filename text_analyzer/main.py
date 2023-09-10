#!/usr/bin/env python3
import os

from time import sleep

from utils.handler import Handler
from utils.news_scraper import NewsScraper
from utils.social_media_scraper import RedditScraper, TwitterScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker

LOGGER = get_logger("Text Analyzer")
MODE = os.getenv("MODE")


def main() -> None:
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
    if reddit_client_id and reddit_client_secret and reddit_user_agent:
        reddit_scraper = RedditScraper(
            reddit_client_id, reddit_client_secret, reddit_user_agent
        )
    else:
        reddit_scraper = None

    tweepy_consumer_key = os.getenv("TWEEPY_CONSUMER_KEY")
    tweepy_consumer_secret = os.getenv("TWEEPY_CONSUMER_SECRET")
    tweepy_access_token = os.getenv("TWEEPY_ACCESS_TOKEN")
    tweepy_access_token_secret = os.getenv("TWEEPY_ACCESS_TOKEN_SECRET")
    if (
        tweepy_consumer_key
        and tweepy_consumer_secret
        and tweepy_access_token
        and tweepy_access_token_secret
    ):
        twitter_scraper = TwitterScraper(
            tweepy_consumer_key,
            tweepy_consumer_secret,
            tweepy_access_token,
            tweepy_access_token_secret,
        )
    else:
        twitter_scraper = None

    text_scraper = NewsScraper()
    text_inference = ClassificationInference(os.getenv("TEXT_INFERENCE_PRETRAINED"))
    publisher = Publisher("text-analyzer-pub", Broker())
    handler = Handler(
        text_scraper, reddit_scraper, twitter_scraper, text_inference, publisher
    )
    subscriber = Subscriber("text-analyzer-sub", Broker(), "slackbot-pub", [handler])
    subscriber.start()


if __name__ == "__main__":
    if MODE != "prod":
        LOGGER.info(f"Running in non-prod mode {MODE}, Sleep forever...")
        while True:
            sleep(60)
    main()
