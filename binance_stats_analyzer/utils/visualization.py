import matplotlib.pyplot as plt

from common_utils.logger import get_logger

LOGGER = get_logger("Utils | Visualization")


def initializePlot(
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
