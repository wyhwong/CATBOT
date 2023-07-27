import pandas as pd

from .stats_analyzer import StatisticalAnalyzer
from .binance_client import BinanceClient
from .visualization import plot_klines, plot_price_prediction
from common_utils.logger import get_logger
from common_utils.mqtt import Publisher, MQTTMessage


LOGGER = get_logger("statistical_analyzer/utils/handler")


class Handler:
    def __init__(self, binance_api: BinanceClient, stats_analyzer: StatisticalAnalyzer, publisher: Publisher) -> None:
        self.publisher = publisher
        self.binance_api = binance_api
        self.stats_analyzer = stats_analyzer
        LOGGER.info("Initialized Statistical Analyzer Handler.")

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        content = mqtt_message.content
        if content.get("scores"):
            self.analyze(content["scores"])
        elif content.get("scommand"):
            getattr(self, content["scommand"])(content["args"])
        else:
            mqtt_message = MQTTMessage.from_str("stats-analyzer-pub", str(content))
            self.publisher.publish(mqtt_message)

    def publish_message(self, message: str) -> None:
        mqtt_message = MQTTMessage.from_str("stats-analyzer-pub", message)
        self.publisher.publish(mqtt_message)

    def analyze(self, target_scores: dict) -> None:
        targets = target_scores.keys()
        price_dfs = self.binance_api.query(targets)
        for target in targets:
            price_max, price_min = price_dfs[target]["Price"].max(), price_dfs[target]["Price"].min()
            norm_price_curr = (price_dfs[target]["Price"].iloc[-1] - price_min) / (price_max - price_min)
            _, norm_price_max_predicts, norm_price_min_predicts = self.stats_analyzer.forecast_price(
                target, price_dfs[target]
            )
            weighting = 100.0 / self.stats_analyzer.target_increase
            score_prediction = (
                norm_price_max_predicts
                - min(norm_price_curr, norm_price_min_predicts)
                - norm_price_curr
                - norm_price_min_predicts
            ) * weighting
            target_scores[target]["stats"] = min(max(-1.0, score_prediction), 1.0)
        message = str({"command": "log", "scores": target_scores})
        self.publish_message(message)

    def show_klines(self, command_args: dict):
        target = command_args["target"].upper()
        duration = float(command_args["duration"])
        LOGGER.info(f"Visualizing klines for {target}...")
        start_str = (pd.Timestamp.now() - pd.Timedelta(hours=duration)).strftime("%Y-%m-%d' %H:%M:%S")
        klines = self.binance_api.get_klines(target, start_str, command_args["interval"])
        plot_klines(klines, target, "/data")
        message = str({"command": "post", "args": {"type": "png", "path": f"/data/{target}_klines.png"}})
        self.publish_message(message)

    def show_last_predict(self, command_args: dict):
        target = command_args["target"].upper()
        LOGGER.info(f"Visualizing the previous prediction")
        price_df = self.binance_api.get_price(
            target, (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime("%Y-%m-%d' %H:%M:%S"), "1d"
        )
        predictions = self.stats_analyzer.forecast.get(target, None)
        plot_price_prediction(price_df, predictions, target, "/data")
        message = str({"command": "post", "args": {"type": "png", "path": f"/data/{target}_prediction.png"}})
        self.publish_message(message)
