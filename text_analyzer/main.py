#!/usr/bin/env python3
import os

from utils.news_scraper import NewsScraper
from utils.social_media_scraper import RedditScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Text Analyzer")


class Handler:
    def __init__(
        self,
        news_scraper: NewsScraper,
        reddit_scraper: RedditScraper,
        text_inference: ClassificationInference,
        publisher: Publisher,
    ) -> None:
        LOGGER.info("Initializing handler...")
        self.publisher = publisher
        self.reddit_scraper = reddit_scraper
        self.text_inference = text_inference
        self.text_scraper = news_scraper
        LOGGER.info("Initialized handler.")

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        target_scores = mqtt_message.content
        LOGGER.info(f"Got target scores from MQTT message: {target_scores}")
        target_reddit_prompts = self.reddit_scraper.scrape(targets=target_scores.keys())
        target_news_prompts = self.text_scraper.scrape(targets=target_scores.keys())
        for target in target_scores.keys():
            target_scores[target]["news"] = self.text_inference.get_score(prompts=target_news_prompts[target])
            target_scores[target]["reddit"] = self.text_inference.get_score(prompts=target_news_prompts[target])
        message = str(target_scores)
        mqtt_message = MQTTMessage.from_str(topic="text-analyzer-pub", message=message)
        self.publisher.publish(message=mqtt_message)
        LOGGER.info("Text analysis done.")


def main() -> None:
    text_scraper = NewsScraper()
    reddit_scraper = RedditScraper(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_RESECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )
    text_inference = ClassificationInference(pretrained=os.getenv("TEXT_INFERENCE_PRETRAINED"))
    publisher = Publisher(client_id="text-analyzer-pub", broker=Broker())
    handler = Handler(
        text_inference=text_inference, news_scraper=text_scraper, reddit_scraper=reddit_scraper, publisher=publisher
    )
    subscriber = Subscriber(client_id="text-analyzer-sub", broker=Broker(), topic="slackbot-pub", handlers=[handler])
    subscriber.start()


if __name__ == "__main__":
    main()
