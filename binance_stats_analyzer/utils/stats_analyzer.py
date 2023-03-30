import pandas as pd
import numpy as np
from darts import TimeSeries
from darts.models.forecasting.auto_arima import AutoARIMA
from darts.models.forecasting.lgbm import LightGBMModel

from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Statistical Analyzer")


def get_analyzer_config() -> dict:
    return read_content_from_yml(path="configs/stats_analyzer/analyzer.yml")


class StatisticalAnalyzer:
    def __init__(self) -> None:
        LOGGER.debug("Initializing statistical analyzer...")
        config = get_analyzer_config()
        self.model_LightGBM = LightGBMModel(lags=10, output_chunk_length=30)
        self.model_AutoARIMA = AutoARIMA(start_p=10, start_q=10)
        self.models = ["AutoARIMA", "LightGBM"]
        if config["enable_LSTM"]:
            from darts.models.forecasting.rnn_model import RNNModel

            self.model_LSTM = RNNModel(
                input_chunk_length=7,
                training_length=365,
                optimizer_kwargs={"lr": 1e-3},
                model="LSTM",
                batch_size=16,
                n_epochs=50,
                force_reset=True,
            )
            self.models.append("LSTM")
        self.forecast, self.forecast_avg_max, self.forecast_avg_min = {}, {}, {}
        self.target_increase = config["target_increase"]
        LOGGER.info("Initialized statistical analyzer.")

    def forecast_price(self, target: str, price_df: pd.DataFrame) -> tuple:
        forecast, forecast_avg_max, forecast_avg_min = {}, 0.0, 0.0
        for model in self.models:
            if model == "LSTM":
                price_max, price_min, time_series = self.transform_price_dataframe(dataframe=price_df, normalize=True)
            else:
                price_max, price_min, time_series = self.transform_price_dataframe(dataframe=price_df)
            getattr(self, f"model_{model}").fit(series=time_series)
            forecast[model] = getattr(self, f"model_{model}").predict(n=30).values()
            model_forecast_avg_max = forecast[model].max()
            forecast_avg_max += model_forecast_avg_max / len(self.models)
            model_forecast_avg_min = forecast[model].min()
            forecast_avg_min += model_forecast_avg_min / len(self.models)
            if model == "LSTM":
                forecast[model] = np.hstack(forecast[model]) * (price_max - price_min) + price_min
            else:
                forecast[model] = np.hstack(forecast[model])
            LOGGER.info(
                f"Predicted by {model}, max in 30 days: {model_forecast_avg_max}, min in 30 days: {model_forecast_avg_min}"
            )
        self.forecast[target], self.forecast_avg_max[target], self.forecast_avg_min[target] = (
            forecast,
            forecast_avg_max,
            forecast_avg_min,
        )
        return (forecast, forecast_avg_max, forecast_avg_min)

    def transform_price_dataframe(self, dataframe: pd.DataFrame, freq="1d", normalize=False) -> tuple:
        price_max, price_min = dataframe["Price"].max(), dataframe["Price"].min()
        if normalize:
            dataframe["Price"] = (dataframe["Price"] - price_min) / (price_max - price_min)
        return (
            price_max,
            price_min,
            TimeSeries.from_dataframe(df=dataframe, time_col="Time", value_cols="Price", freq=freq),
        )
