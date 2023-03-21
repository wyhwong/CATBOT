#!/usr/bin/env python3
import os

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
        targets = target_scores.keys()

        price_dfs = self.binance_api.query(targets=targets)
        for target in targets:
            price_max, price_min, time_series = self.stats_analyzer.transform_price_dataframe(
                dataframe=price_dfs[target]
            )
            norm_price_curr = (time_series.values()[-1][0] - price_min) / (price_max - price_min)
            _, norm_price_max_predicts, norm_price_min_predicts = self.stats_analyzer.forecast_price(
                target=target, time_series=time_series
            )
            weighting = 100.0 / self.stats_analyzer.target_increase
            score_prediction = (
                norm_price_max_predicts
                - min(norm_price_curr, norm_price_min_predicts)
                - norm_price_curr
                - norm_price_min_predicts
            ) * weighting
            target_scores[target]["stats"] = min(1, score_prediction)
        message = str({"command": "log", "scores": target_scores})
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
