import pandas as pd
from copy import deepcopy
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
        self.model_LightGBM = RNNModel(input_chunk_length=30, model="LSTM", batch_size=16, n_epochs=50)
        self.models = ["LSTM", "AutoARIMA", "LightGBM"]
        self.forecast, self.forecast_avg_max, self.forecast_avg_min = {}, {}, {}
        self.last_analysis_date = None
        self.target_increase = get_analyzer_config()["target_increase"]

    def forecast_price(self, target, time_series: TimeSeries) -> tuple:
        date_curr = pd.Timestamp.now().date()
        if self.forecast.get(target) and self.last_analysis_date == date_curr:
            LOGGER.info("Prediction exists, read from cached data.")
            return (self.forecast.get(target), self.forecast_avg_max.get(target), self.forecast_avg_min.get(target))

        self.last_analysis_date = date_curr
        forecast, forecast_avg_max, forecast_avg_min = {}, 0.0, 0.0
        for model in self.models:
            model_in_use = deepcopy(getattr(self, f"model_{model}"))
            model_in_use.fit(series=time_series)
            forecast[model] = model_in_use.predict(n=30)
            model_forecast_avg_max = forecast[model].values().max()
            forecast_avg_max += model_forecast_avg_max / len(self.models)
            model_forecast_avg_min = forecast[model].values().min()
            forecast_avg_min += model_forecast_avg_min / len(self.models)
            LOGGER.info(
                f"Predicted by {model}, max in 30 days: {model_forecast_avg_max}, min in 30 days: {model_forecast_avg_min}"
            )
        self.forecast[target], self.forecast_avg_max[target], self.forecast_avg_min[target] = (
            forecast,
            forecast_avg_max,
            forecast_avg_min,
        )
        return (forecast, forecast_avg_max, forecast_avg_min)

    def transform_price_dataframe(self, dataframe: pd.DataFrame, freq="1d") -> tuple:
        price_max, price_min = dataframe["Price"].max(), dataframe["Price"].min()
        dataframe["Price"] = (dataframe["Price"] - price_min) / (price_max - price_min)
        return (
            price_max,
            price_min,
            TimeSeries.from_dataframe(df=dataframe, time_col="Time", value_cols="Price", freq=freq),
        )
