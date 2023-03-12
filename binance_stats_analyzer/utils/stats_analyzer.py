import darts
import pandas as pd

from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Statistical Analyzer")


def get_analyzer_config() -> dict:
    return read_content_from_yml(path="configs/analyzer.yml")


class StatisticalAnalyzer:
    def __init__(self) -> None:
        pass

    def analyze(kline_df: pd.DataFrame, num_trade_df: pd.DataFrame) -> float:
        pass
