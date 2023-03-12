#!/usr/bin/env python3
import os

from utils.text_scraper import TextScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Text Analyzer")


class Handler:
    def __init__(
        self, text_scraper: TextScraper, text_inference: ClassificationInference, publisher: Publisher
    ) -> None:
        LOGGER.info("Initializing handler...")
        self.publisher = publisher
        self.text_inference = text_inference
        self.text_scraper = text_scraper
        LOGGER.info("Initialized handler.")

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        target_scores = mqtt_message.content
        LOGGER.info(f"Got target scores from MQTT message: {target_scores}")
        target_prompts = self.text_scraper(targets=target_scores.keys())
        for target in target_scores.keys():
            prompts = target_prompts[target]
            target_scores[target]["text"] = self.text_inference.get_score(prompts=prompts)
        message = str(target_scores)
        mqtt_message = MQTTMessage.from_str(topic="text-analyzer-pub", message=message)
        self.publisher.publish(message=mqtt_message)
        LOGGER.info("Text analysis done.")


def main() -> None:
    text_scarper = TextScraper()
    pretrained = os.getenv("TEXT_INFERENCE_PRETRAINED")
    text_inference = ClassificationInference(pretrained=pretrained)
    publisher = Publisher(client_id="text-analyzer-pub", broker=Broker())
    handler = Handler(text_inference=text_inference, text_scraper=text_scarper, publisher=publisher)
    subscriber = Subscriber(client_id="text-analyzer-sub", broker=Broker(), topic="slackbot-pub", handlers=[handler])
    subscriber.start()


if __name__ == "__main__":
    main()
