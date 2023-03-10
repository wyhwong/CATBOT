from common_utils.mqtt import Publisher, MQTTMessage
from common_utils.logger import get_logger
from utils.stats_analyzer import StatisticalAnalyzer
from utils.binance_client import BinanceClient

LOGGER = get_logger(logger_name="Utils | Handler")


class Handler:
    def __init__(self, binance_api: BinanceClient, stats_analyzer: StatisticalAnalyzer, publisher: Publisher) -> None:
        self.publisher = publisher
        self.binance_api = binance_api
        self.stats_analyzer = stats_analyzer

    def on_MQTTMessage(self, mqtt_message) -> None:
        mqtt_message.decode_payload()
        kline_dfs, num_trade_dfs = self.binance_api.query(targets=mqtt_message.content["targets"])
        self.stats_analyzer.analyze(kline_dfs=kline_dfs, num_trade_dfs=num_trade_dfs)
        message = MQTTMessage()
        self.publisher.publish(message=mqtt_message)
