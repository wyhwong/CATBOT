import os
import pandas as pd
from binance.client import Client


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.client = Client(api_key=api_key,
                             api_secret=api_secret)

    def _get_historical_data(self, symbol: str, start_str: str, end_str: str, interval="5m"):
        dataframe = self.client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str, end_str=end_str)
        return pd.DataFrame(dataframe)

    def get_klines(self, symbol: str, start_str: str, end_str: str, interval="5m") -> pd.DataFrame:
        dataframe = self._get_historical_data(symbol=symbol,
                                              start_str=start_str,
                                              end_str=end_str,
                                              interval=interval).loc[:,:5]
        dataframe.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
        return dataframe.set_index(pd.to_datetime(dataframe["Time"], unit="ms")).astype(float)

    def get_number_of_trade(self, symbol: str, start_str: str, end_str: str, interval="5m") -> pd.DataFrame:
        dataframe = self._get_historical_data(symbol=symbol,
                                              start_str=start_str,
                                              end_str=end_str,
                                              interval=interval).loc[0:,(0,8)]
        dataframe.columns = ["Time", "Number_of_Trades"]
        return dataframe.set_index(pd.to_datetime(dataframe["Time"], unit="ms")).astype(float)

    def query(self, targets: list) -> tuple:
        kline_dataframes = []
        num_trades_dataframes = []
        start_str = str(pd.Timestamp.now())
        end_str = str(pd.Timestamp.now() - pd.Timedelta(hours=6))
        for target in targets:
            kline_dataframe = self.get_klines(symbol=target, start_str=start_str, end_str=end_str, interval="5m")
            num_trades_dataframe = self.get_number_of_trade(symbol=target, start_str=start_str, end_str=end_str, interval="5m")
            kline_dataframes.append(kline_dataframe), num_trades_dataframes.append(num_trades_dataframe)
        return (kline_dataframes, num_trades_dataframes)
