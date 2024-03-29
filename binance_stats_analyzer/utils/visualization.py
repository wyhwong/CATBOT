import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import numpy as np

from dataclasses import dataclass
from common_utils.logger import get_logger
from common_utils.common import check_and_create_dir

LOGGER = get_logger("statistical_analyzer/utils/visualization")


@dataclass
class Padding:
    """
    Padding of the plot.

    Attributes:
        tpad (float): Top padding.
        lpad (float): Left padding.
        bpad (float): Bottom padding.
    """

    tpad: float = 2.5
    lpad: float = 0.1
    bpad: float = 0.12


@dataclass
class Labels:
    """
    Labels of the plot.

    Attributes:
        title (str): Title of the plot.
        xlabel (str): Label of x-axis.
        ylabel (str): Label of y-axis.
        zlabel (str): Label of z-axis.
    """

    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    zlabel: str = ""


def initialize_plot(
    nrows=1, ncols=1, figsize=(10, 6), labels=Labels(), padding=Padding(), fontsize=12
):
    """
    Initialize plot.

    Args:
        nrows (int): Number of rows of the plot.
        ncols (int): Number of columns of the plot.
        figsize (tuple): Size of the plot.
        labels (Labels): Labels of the plot.
        padding (Padding): Padding of the plot.
        fontsize (int): Font size of the plot.
    Returns:
        fig (matplotlib.figure.Figure): Figure of the plot.
        axes (numpy.ndarray): Axes of the plot.
    """
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    fig.tight_layout(pad=padding.tpad)
    fig.subplots_adjust(left=padding.lpad, bottom=padding.bpad)
    fig.suptitle(labels.title, fontsize=fontsize)
    fig.text(
        x=0.04,
        y=0.5,
        s=labels.ylabel,
        fontsize=fontsize,
        rotation="vertical",
        verticalalignment="center",
    )
    fig.text(
        x=0.5, y=0.04, s=labels.xlabel, fontsize=fontsize, horizontalalignment="center"
    )
    return fig, axes


def savefig_and_close(filename: str, output_dir=None, close=True) -> None:
    """
    Save the plot and close it.

    Args:
        filename (str): Filename of the plot.
        output_dir (str): Output directory of the plot.
        close (bool): Whether to close the plot.
    Returns:
        None.
    """
    if output_dir:
        check_and_create_dir(output_dir)
        savepath = f"{output_dir}/{filename}"
        plt.savefig(savepath, facecolor="w")
        LOGGER.info(f"Saved plot at {savepath}.")
    if close:
        plt.close()


def plot_klines(klines: pd.DataFrame, target: str, output_dir=None, close=True) -> None:
    """
    Plot klines of the target.

    Args:
        klines (pd.DataFrame): Dataframe of the klines.
        target (str): Target cryptocurrency.
        output_dir (str): Output directory of the plot.
        close (bool): Whether to close the plot.
    Returns:
        None.
    """
    LOGGER.info(f"Plotting kine of {target}...")
    labels = Labels(target)
    _, ax = initialize_plot(labels=labels)
    mpf.plot(data=klines, type="candle", show_nontrading=True, ax=ax)
    savefig_and_close(f"{target}_klines.png", output_dir, close)


def plot_price_prediction(
    price_df: pd.DataFrame, predictions: dict, target: str, output_dir=None, close=True
) -> None:
    """
    Plot price prediction of the target.

    Args:
        price_df (pd.DataFrame): Dataframe of the price.
        predictions (dict): Predictions of the price.
        target (str): Target cryptocurrency.
        output_dir (str): Output directory of the plot.
        close (bool): Whether to close the plot.
    Returns:
        None.
    """
    labels = Labels(f"{target} latest forecasting")
    _, ax = initialize_plot(labels=labels)
    sns.lineplot(data=price_df, x="Time", y="Price", ax=ax, label="Real data")
    if predictions:
        for model, price_prediction in predictions.items():
            price_prediction = np.insert(
                price_prediction, 0, price_df["Price"].iloc[-1]
            )
            prediction_time = pd.date_range(
                start=price_df["Time"].iloc[-1], freq="1d", periods=31
            )
            prediction_df = pd.DataFrame(
                {"Time": prediction_time, "Price": price_prediction}
            )
            sns.lineplot(
                data=prediction_df,
                x="Time",
                y="Price",
                ax=ax,
                label=f"Prediction ({model})",
            )
    savefig_and_close(f"{target}_prediction.png", output_dir, close)
