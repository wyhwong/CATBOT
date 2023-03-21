#!/usr/bin/env python3
import os

from utils.handler import Handler
from utils.stats_analyzer import StatisticalAnalyzer
from utils.binance_client import BinanceClient
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker, MQTTMessage

LOGGER = get_logger(logger_name="Main | Statistical Analyzer")


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
