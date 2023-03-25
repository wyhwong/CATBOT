import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import numpy as np

from common_utils.logger import get_logger

LOGGER = get_logger("Utils | Visualization")


def initialize_plot(
    nrows=1, ncols=1, height=6, width=10, title="", xlabel="", ylabel="", tpad=2.5, lpad=0.1, bpad=0.12, fontsize=12
):
    LOGGER.debug(
        f"Initializing plot, {nrows=}, {ncols=}, {height=}, {width=}, {title=}, {xlabel=}, {ylabel=}, {tpad=}, {lpad=}, {bpad=}, {fontsize=}."
    )
    fig, axes = plt.subplots(nrows, ncols, figsize=(width, height))
    fig.tight_layout(pad=tpad)
    fig.subplots_adjust(left=lpad, bottom=bpad)
    fig.suptitle(title, fontsize=fontsize)
    fig.text(x=0.04, y=0.5, s=ylabel, fontsize=fontsize, rotation="vertical", verticalalignment="center")
    fig.text(x=0.5, y=0.04, s=xlabel, fontsize=fontsize, horizontalalignment="center")
    LOGGER.info("Initialized plot.")
    return fig, axes


def plot_klines(klines: pd.DataFrame, target: str, output_dir=None, savefig=False, close=True) -> None:
    LOGGER.info(f"Plotting kine of {target}...")
    _, ax = initialize_plot(nrows=1, ncols=1, height=6, width=10, title=f"{target}")
    mpf.plot(data=klines, type="candle", show_nontrading=True, ax=ax)
    if savefig:
        if output_dir is None:
            raise ValueError("outputDir must not be empty if savefig is True.")
        savepath = f"{output_dir}/{target}_klines.png"
        LOGGER.debug(f"Saving plot at {savepath}.")
        plt.savefig(savepath, facecolor="w")
        LOGGER.info(f"Saved plot at {savepath}.")
    if close:
        LOGGER.debug(f"Closed plot.")
        plt.close()
    LOGGER.info(f"Plotted kine of {target}.")


def plot_price_prediction(
    price_df: pd.DataFrame, predictions: dict, target: str, output_dir=None, savefig=False, close=True
) -> None:
    _, ax = initialize_plot(nrows=1, ncols=1, height=6, width=10, title=f"{target} latest forecasting")
    sns.lineplot(data=price_df, x="Time", y="Price", ax=ax, label="Real data")
    if predictions:
        for model, price_prediction in predictions.items():
            price_prediction = np.insert(price_prediction, 0, price_df["Price"].iloc[-1])
            prediction_time = pd.date_range(start=price_df["Time"].iloc[-1], freq="1d", periods=31)
            prediction_df = pd.DataFrame({"Time": prediction_time, "Price": price_prediction})
            sns.lineplot(data=prediction_df, x="Time", y="Price", ax=ax, label=f"Prediction ({model})")
    if savefig:
        if output_dir is None:
            raise ValueError("outputDir must not be empty if savefig is True.")
        savepath = f"{output_dir}/{target}_prediction.png"
        LOGGER.debug(f"Saving plot at {savepath}.")
        plt.savefig(savepath, facecolor="w")
        LOGGER.info(f"Saved plot at {savepath}.")
    if close:
        LOGGER.debug(f"Closed plot.")
        plt.close()
    LOGGER.info(f"Plotted prediction of {target}.")
