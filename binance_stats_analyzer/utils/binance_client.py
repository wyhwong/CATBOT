import pandas as pd
from binance.client import Client

from .stats_analyzer import get_analyzer_config
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | BinanceAPI")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str) -> None:
        LOGGER.info("Initializing Binance client...")
        self.client = Client(api_key=api_key, api_secret=api_secret)
        config = get_analyzer_config()
        self.interval = config["interval"]
        self.duration_in_days = config["duration_in_days"]
        LOGGER.info("Initialized Binance client...")

    def _get_historical_data(self, symbol: str, start_str: str, interval: str):
        dataframe = pd.DataFrame(
            self.client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str)
        ).astype(float)
        dataframe.columns = [
            "OpenTime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "CloseTime",
            "QuoteAssetVolume",
            "NumberOfTrades",
            "TakerBuyBaseAssetVolume",
            "TakerBuyQuoteAssetVolume",
            "Ignore",
        ]
        dataframe = dataframe.drop(columns="Ignore")
        dataframe["OpenTime"] = pd.to_datetime(dataframe["OpenTime"], unit="ms")
        dataframe["CloseTime"] = pd.to_datetime(dataframe["CloseTime"], unit="ms")
        return dataframe

    def get_klines(self, symbol: str, start_str: str, interval: str) -> pd.DataFrame:
        dataframe = self._get_historical_data(symbol=symbol, start_str=start_str, interval=interval)
        dataframe = dataframe.set_index("OpenTime", drop=False)
        return dataframe[["OpenTime", "Open", "High", "Low", "Close", "Volume"]]

    def get_number_of_trade(self, symbol: str, start_str: str, interval: str) -> pd.DataFrame:
        dataframe = self._get_historical_data(symbol=symbol, start_str=start_str, interval=interval)
        return dataframe[["OpenTime", "NumberOfTrades"]]

    def get_price(self, symbol: str, start_str: str, interval: str) -> pd.DataFrame:
        dataframe = self._get_historical_data(symbol=symbol, start_str=start_str, interval=interval)
        dataframe = dataframe[["OpenTime", "Open"]]
        dataframe.columns = ["Time", "Price"]
        return dataframe

    def query(self, targets: list) -> tuple:
        price_dataframes = {}
        start_str = (pd.Timestamp.now() - pd.Timedelta(days=self.duration_in_days)).strftime("%Y-%m-%d' %H:%M:%S")
        LOGGER.info(f"Querying data from Binance, {start_str=}, {targets=}...")
        for target in targets:
            price_dataframes[target] = self.get_price(symbol=target, start_str=start_str, interval=self.interval)
            LOGGER.info(f"Queried data of {target} from Binance.")
        return price_dataframes
