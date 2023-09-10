#!/usr/bin/env python3
import os

from time import sleep
from utils.handler import Handler
from utils.stats_analyzer import StatisticalAnalyzer
from utils.binance_client import BinanceClient
from common_utils.logger import get_logger
from common_utils.mqtt import Subscriber, Publisher, Broker

LOGGER = get_logger("Statistical Analyzer")
MODE = os.getenv("MODE")


def main() -> None:
    publisher = Publisher("stats-analyzer-pub", Broker())
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")
    binance_api = BinanceClient(binance_api_key, binance_api_secret)
    stats_analyzer = StatisticalAnalyzer()
    handler = Handler(binance_api, stats_analyzer, publisher)
    subscriber = Subscriber(
        "stats-analyzer-sub", Broker(), "text-analyzer-pub", [handler]
    )
    subscriber.start()


if __name__ == "__main__":
    if MODE != "prod":
        LOGGER.info(f"Running in non-prod mode {MODE}, Sleep forever...")
        while True:
            sleep(60)
    main()
