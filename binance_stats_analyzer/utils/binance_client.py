import os
import pandas as pd
from binance.client import Client

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.client = Client(api_key=api_key,
                             api_secret=api_secret)

    def get_klines(self, symbol: str, interval: str, start_str: str, end_str: str) -> pd.DataFrame:
        dataframe = self.client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str, end_str=end_str)
        dataframe = pd.DataFrame(dataframe).iloc[:, :6]
        dataframe.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        return dataframe.set_index(pd.DatetimeIndex(dataframe["date"])).astype(float)

    def get_time_series(self) -> pd.DataFrame:
        pass