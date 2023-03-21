from .news_scraper import NewsScraper
from .social_media_scraper import RedditScraper, TwitterScraper
from .classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Publisher, MQTTMessage

LOGGER = get_logger(logger_name="Utils | Handler")


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
        content = mqtt_message.content
        if content.get("scores"):
            self.analyze(target_scores=content)
        elif content.get("tcommand"):
            getattr(self, content["tcommand"])(content=content)
        else:
            mqtt_message = MQTTMessage.from_str(topic="text-analyzer-pub", message=str(content))
            self.publisher.publish(message=mqtt_message)

    def analyze(self, target_scores: dict) -> None:
        targets = target_scores.keys()
        LOGGER.info(f"Got target scores from MQTT message: {target_scores}")
        target_news_prompts = self.text_scraper.scrape(targets=targets)
        if self.reddit_scraper:
            target_reddit_prompts = self.reddit_scraper.scrape(targets=targets)
        if self.twitter_scraper:
            target_twitter_prompts = self.twitter_scraper.scrape(targets=targets)

        for target in targets:
            if target_news_prompts[target]:
                target_scores[target]["news"] = self.text_inference.get_score(prompts=target_news_prompts[target])
            if self.reddit_scraper and target_reddit_prompts[target]:
                target_scores[target]["reddit"] = self.text_inference.get_score(prompts=target_reddit_prompts[target])
            if self.twitter_scraper and target_twitter_prompts[target]:
                target_scores[target]["twitter"] = self.text_inference.get_score(prompts=target_twitter_prompts[target])
        message = str(target_scores)
        mqtt_message = MQTTMessage.from_str(topic="text-analyzer-pub", message=message)
        self.publisher.publish(message=mqtt_message)
        LOGGER.info("Text analysis done.")
