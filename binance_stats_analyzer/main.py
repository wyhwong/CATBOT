#!/usr/bin/env python3
import os

from utils.handler import Handler
from utils.stats_analyzer import StatisticalAnalyzer
from utils.binance_client import BinanceClient
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Statistical Analyzer")


class Handler:
    def __init__(self, binance_api: BinanceClient, stats_analyzer: StatisticalAnalyzer, publisher: Publisher) -> None:
        self.publisher = publisher
        self.binance_api = binance_api
        self.stats_analyzer = stats_analyzer

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        target_scores = mqtt_message.content
        kline_dfs, num_trade_dfs = self.binance_api.query(targets=target_scores.keys())
        for idx, target in enumerate(target_scores.keys()):
            target_scores[target]["stat"] = self.stats_analyzer.analyze(kline_df=kline_dfs[idx], num_trade_df=num_trade_dfs[idx])
        message = str(target_scores)
        mqtt_message = MQTTMessage.from_str(topic="stats-analyzer-pub", message=message)
        self.publisher.publish(message=mqtt_message)


def main() -> None:
    publisher = Publisher(client_id="stats-analyzer-pub", broker=Broker())
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")
    binance_api = BinanceClient(api_key=binance_api_key, api_secret=binance_api_secret)
    stats_analyzer = StatisticalAnalyzer()
    handler = Handler(binance_api=binance_api, stats_analyzer=stats_analyzer, publisher=publisher)
    subscriber = Subscriber(
        client_id="stats-analyzer-sub", broker=Broker(), topic="text-analyzer-pub", handlers=[handler]
    )
    subscriber.start()


if __name__ == "__main__":
    main()
