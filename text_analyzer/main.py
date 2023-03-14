#!/usr/bin/env python3
import os

from utils.news_scraper import NewsScraper
from utils.social_media_scraper import RedditScraper, TwitterScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Text Analyzer")


class Handler:
    def __init__(
        self,
        news_scraper: NewsScraper,
        reddit_scraper: RedditScraper,
        twitter_scraper: TwitterScraper,
        text_inference: ClassificationInference,
        publisher: Publisher,
    ) -> None:
        LOGGER.info("Initializing handler...")
        self.publisher = publisher
        self.reddit_scraper = reddit_scraper
        self.twitter_scraper = twitter_scraper
        self.text_inference = text_inference
        self.text_scraper = news_scraper
        LOGGER.info("Initialized handler.")

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        target_scores = mqtt_message.content
        targets = target_scores.keys()
        LOGGER.info(f"Got target scores from MQTT message: {target_scores}")
        if self.reddit_scraper:
            target_reddit_prompts = self.reddit_scraper.scrape(targets=targets)
        if self.twitter_scraper:
            target_twitter_prompts = self.twitter_scraper.scrape(targets=targets)
        target_news_prompts = self.text_scraper.scrape(targets=targets)

        for target in targets:
            target_scores[target]["news"] = self.text_inference.get_score(prompts=target_news_prompts[target])
            if self.reddit_scraper:
                target_scores[target]["reddit"] = self.text_inference.get_score(prompts=target_reddit_prompts[target])
            if self.twitter_scraper:
                target_scores[target]["twitter"] = self.text_inference.get_score(prompts=target_twitter_prompts[target])
        message = str(target_scores)
        mqtt_message = MQTTMessage.from_str(topic="text-analyzer-pub", message=message)
        self.publisher.publish(message=mqtt_message)
        LOGGER.info("Text analysis done.")


def main() -> None:
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_RESECRET")
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
    tweepy_consumer_secret = os.getenv("TWEEPY_CONSUMER_KEY")
    tweepy_access_token = os.getenv("TWEEPY_CONSUMER_KEY")
    tweepy_access_token_secret = os.getenv("TWEEPY_CONSUMER_KEY")
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
