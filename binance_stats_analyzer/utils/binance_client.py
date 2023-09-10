import pandas as pd
from binance.client import Client

from utils.stats_analyzer import get_analyzer_config
from common_utils.logger import get_logger

LOGGER = get_logger("statistical_analyzer/utils/binance_client")


class BinanceClient:
    """
    Binance client for querying data from Binance.

    Attributes:
        client (binance.client.Client): Binance client.
        interval (str): Interval of klines.
        duration_in_days (str): Duration of klines in days.
    """

    def __init__(self, api_key: str, api_secret: str) -> None:
        """
        Initialize Binance client.

        Args:
            api_key (str): API key of Binance.
            api_secret (str): API secret of Binance.
        Returns:
            None.
        """
        self.client = Client(api_key, api_secret)
        config = get_analyzer_config()
        self.interval = config["interval"]
        self.duration_in_days = config["duration_in_days"]
        LOGGER.info("Initialized Binance client...")

    def _get_historical_data(
        self, symbol: str, start: str, interval: str
    ) -> pd.DataFrame:
        """
        Get historical data from Binance.

        Args:
            symbol (str): Symbol of the cyrptocurrency on Binance.
            start_str (str): Start time of the data.
            interval (str): Interval of the data.
        Returns:
            Dataframe of the historical data (pd.DataFrame).
        """
        dataframe = pd.DataFrame(
            self.client.get_historical_klines(symbol, interval, start)
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

    def get_klines(self, symbol: str, start: str, interval: str) -> pd.DataFrame:
        """
        Get klines from Binance.

        Args:
            symbol (str): Symbol of the cyrptocurrency on Binance.
            start (str): Start time of the data.
            interval (str): Interval of the data.
        Returns:
            Dataframe of the klines (pd.DataFrame).
        """
        dataframe = self._get_historical_data(
            symbol=symbol, start=start, interval=interval
        )
        dataframe = dataframe.set_index("OpenTime", drop=False)
        return dataframe[["OpenTime", "Open", "High", "Low", "Close", "Volume"]]

    def get_number_of_trade(
        self, symbol: str, start: str, interval: str
    ) -> pd.DataFrame:
        """
        Get number of trades from Binance.

        Args:
            symbol (str): Symbol of the cyrptocurrency on Binance.
            start (str): Start time of the data.
            interval (str): Interval of the data.
        Returns:
            Dataframe of the number of trades (pd.DataFrame).
        """
        dataframe = self._get_historical_data(symbol, start, interval)
        return dataframe[["OpenTime", "NumberOfTrades"]]

    def get_price(self, symbol: str, start: str, interval: str) -> pd.DataFrame:
        """
        Get price from Binance.

        Args:
            symbol (str): Symbol of the cyrptocurrency on Binance.
            start (str): Start time of the data.
            interval (str): Interval of the data.
        Returns:
            Dataframe of the price (pd.DataFrame).
        """
        dataframe = self._get_historical_data(symbol, start, interval)
        dataframe = dataframe[["OpenTime", "Open"]]
        dataframe.columns = ["Time", "Price"]
        return dataframe

    def query(self, targets: list) -> tuple:
        """
        Query data from Binance.

        Args:
            targets (list): List of symbols of the cyrptocurrencies on Binance.
        Returns:
            Dataframes of prices of the list of cyrptocurrencies (dict).
        """
        price_dataframes = {}
        start = (
            pd.Timestamp.now() - pd.Timedelta(days=self.duration_in_days)
        ).strftime("%Y-%m-%d' %H:%M:%S")
        LOGGER.info(f"Querying data from Binance, {start=}, {targets=}...")
        for target in targets:
            price_dataframes[target] = self.get_price(target, start, self.interval)
        return price_dataframes
