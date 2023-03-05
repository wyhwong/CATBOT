#!/usr/bin/env python3
import os

from utils.text_scraper import TextScraper
from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Text Analyzer")


class Handler:
    def __init__(self,
                 text_scraper: TextScraper,
                 text_inference: ClassificationInference,
                 publisher: Publisher) -> None:
        self.publisher = publisher
        self.text_inference = text_inference
        self.text_scraper = text_scraper

    def on_MQTTMessage(self, mqtt_message) -> None:
        prompts = self.text_scraper(target=mqtt_message)
        inference_score = 0
        for prompt in prompts:
            inference_score += self.text_inference(prompt=prompt) / len(prompts)
        mqtt_message = MQTTMessage.from_str(topic="slackbot-sub", message=inference_score)
        self.publisher.publish(message=mqtt_message)


def main() -> None:
    text_scarper = TextScraper()
    pretrained = os.getenv("TEXT_INFERENCE_PRETRAINED")
    text_inference = ClassificationInference(pretrained=pretrained)
    publisher = Publisher(client_id="text-analyzer-pub",
                          broker=Broker())
    handler = Handler(text_inference=text_inference,
                      text_scraper=text_scarper,
                      publisher=publisher)
    subscriber = Subscriber(client_id="text-analyzer-sub",
                            broker=Broker(),
                            topic="slackbot-pub",
                            handlers=[handler])
    subscriber.start()


if __name__ == "__main__":
    main()
