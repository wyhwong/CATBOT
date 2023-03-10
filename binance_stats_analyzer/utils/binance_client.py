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
        self.duration_in_hrs = config["duration"]
        LOGGER.info("Initialized Binance client...")

    def _get_historical_data(self, symbol: str, start_str: str, end_str: str, interval):
        dataframe = self.client.get_historical_klines(
            symbol=symbol, interval=interval, start_str=start_str, end_str=end_str
        )
        return pd.DataFrame(dataframe)

    def get_klines(self, symbol: str, start_str: str, end_str: str, interval) -> pd.DataFrame:
        dataframe = self._get_historical_data(
            symbol=symbol, start_str=start_str, end_str=end_str, interval=interval
        ).loc[:, :5]
        dataframe.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
        return dataframe.set_index(pd.to_datetime(dataframe["Time"], unit="ms")).astype(float)

    def get_number_of_trade(self, symbol: str, start_str: str, end_str: str, interval) -> pd.DataFrame:
        dataframe = self._get_historical_data(
            symbol=symbol, start_str=start_str, end_str=end_str, interval=interval
        ).loc[0:, (0, 8)]
        dataframe.columns = ["Time", "Number_of_Trades"]
        return dataframe.set_index(pd.to_datetime(dataframe["Time"], unit="ms")).astype(float)

    def query(self, targets: list) -> tuple:
        kline_dataframes = []
        num_trades_dataframes = []
        start_str = str(pd.Timestamp.now())
        end_str = str(pd.Timestamp.now() - pd.Timedelta(hours=self.duration_in_hrs))
        LOGGER.info(f"Querying data from Binance, {start_str=}, {end_str=}, {targets=}...")
        for target in targets:
            kline_dataframe = self.get_klines(
                symbol=target, start_str=start_str, end_str=end_str, interval=self.interval
            )
            num_trades_dataframe = self.get_number_of_trade(
                symbol=target, start_str=start_str, end_str=end_str, interval=self.interval
            )
            kline_dataframes.append(kline_dataframe), num_trades_dataframes.append(num_trades_dataframe)
            LOGGER.info(f"Queried data of {target} from Binance.")
        return (kline_dataframes, num_trades_dataframes)
