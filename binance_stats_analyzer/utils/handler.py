from .stats_analyzer import StatisticalAnalyzer
from .binance_client import BinanceClient
from common_utils.logger import get_logger
from common_utils.mqtt import Publisher, MQTTMessage


LOGGER = get_logger(logger_name="utils | handler")


class Handler:
    def __init__(self, binance_api: BinanceClient, stats_analyzer: StatisticalAnalyzer, publisher: Publisher) -> None:
        self.publisher = publisher
        self.binance_api = binance_api
        self.stats_analyzer = stats_analyzer

    def on_MQTTMessage(self, mqtt_message: MQTTMessage) -> None:
        mqtt_message.decode_payload()
        content = mqtt_message.content
        if content.get("scores"):
            self.analyze(target_scores=content)
        elif content.get("scommand"):
            getattr(self, content["scommand"])(content=content)
        else:
            mqtt_message = MQTTMessage.from_str(topic="stats-analyzer-pub", message=str(content))
            self.publisher.publish(message=mqtt_message)

    def analyze(self, target_scores: dict) -> None:
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
