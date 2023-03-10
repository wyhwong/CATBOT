import matplotlib.pyplot as plt
import mplfinance as mpf

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


def plot_klines(klines: list, targets: list, output_dir=None, savefig=False, close=True):
    for idx, kline in enumerate(klines):
        LOGGER.info(f"Plotting kine of {targets[idx]}...")
        _, ax = initialize_plot(nrows=1, ncols=1, height=6, width=10, title=f"{targets[idx]}")
        mpf.plot(data=kline, type="candle", show_nontrading=True, ax=ax)
        if savefig:
            if output_dir is None:
                raise ValueError("outputDir must not be empty if savefig is True.")
            savepath = f"{output_dir}/{targets[idx]}_kline.png"
            LOGGER.debug(f"Saving plot at {savepath}.")
            plt.savefig(savepath, facecolor="w")
            LOGGER.info(f"Saved plot at {savepath}.")
        if close:
            LOGGER.debug(f"Closed plot.")
            plt.close()
        LOGGER.info(f"Plotted kine of {targets[idx]}.")
