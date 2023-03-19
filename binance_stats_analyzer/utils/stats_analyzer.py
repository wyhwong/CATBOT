import pandas as pd
from darts import TimeSeries
from darts.models.forecasting.auto_arima import AutoARIMA
from darts.models.forecasting.lgbm import LightGBMModel
from darts.models.forecasting.rnn_model import RNNModel

from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Statistical Analyzer")


def get_analyzer_config() -> dict:
    return read_content_from_yml(path="configs/analyzer.yml")


class StatisticalAnalyzer:
    def __init__(self) -> None:
        self.model_LSTM = LightGBMModel(lags=1)
        self.model_AutoARIMA = AutoARIMA()
        self.model_LightGBM = RNNModel(input_chunk_length=30, model="LSTM")
        self.models = ["LSTM", "AutoARIMA", "LightGBM"]
        self.forecast, self.forecast_avg_max, self.forecast_avg_min = None, None, None
        self.last_analysis_date = None
        self.score_factor = get_analyzer_config()["score_factor"]

    def forecast(self, time_series: TimeSeries) -> tuple:
        date_curr = pd.Timestamp.now().date()
        if self.forecast and self.last_analysis_date == date_curr:
            return (self.forecast, self.forecast_avg_max, self.forecast_avg_min)

        self.last_analysis_date = date_curr
        forecast, forecast_avg_max, forecast_avg_min = {}, 0., 0.
        for model in self.models:
            model_in_use = getattr(self, f"model_{model}").copy()
            model_in_use.fit(series=time_series)
            forecast[model] = model_in_use.predict(n=30)
            forecast_avg_max += forecast[model].values().max() / len(self.models)
            forecast_avg_min += forecast[model].values().min() / len(self.models)
        self.forecast, self.forecast_avg_max, self.forecast_avg_min = forecast, forecast_avg_max, forecast_avg_min
        return (forecast, forecast_avg_max, forecast_avg_min)

    def transform_price_dataframe(dataframe: pd.DataFrame, freq="1d") -> tuple:
        price_max, price_min = dataframe["Price"].max(), dataframe["Price"].min()
        dataframe["Price"] = (dataframe["Price"] - price_min) / (price_max - price_min)
        return (price_max, price_min, TimeSeries.from_dataframe(df=dataframe, time_col="Time", value_cols="Price", freq=freq))