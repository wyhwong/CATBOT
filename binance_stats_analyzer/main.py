#!/usr/bin/env python3
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Stats Analyzer")


class Handler:
    def __init__(self, binance_api, stats_analyzer, publisher: Publisher) -> None:
        self.publisher = publisher
        self.binance_api = binance_api
        self.stats_analyzer = stats_analyzer

    def on_MQTTMessage(self, mqtt_message) -> None:
        self.binance_api.query()
        self.stats_analyzer.analyze()
        message = MQTTMessage()
        self.publisher.publish(message=mqtt_message)


def main() -> None:
    publisher = Publisher(client_id="stats-analyzer-pub", broker=Broker())
    # TODO:
    binance_api = None
    stats_analyzer = None
    handler = Handler(binance_api=binance_api, stats_analyzer=stats_analyzer, publisher=publisher)
    subscriber = Subscriber(client_id="stats-analyzer-sub", broker=Broker(), topic="slackbot-pub", handlers=[handler])
    subscriber.start()


if __name__ == "__main__":
    main()
