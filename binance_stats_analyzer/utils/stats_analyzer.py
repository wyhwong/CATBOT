import darts
from common_utils.common import read_content_from_yml
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Utils | Statistical Analyzer")


def get_analyzer_config():
    return read_content_from_yml(path="configs/analyzer.yml")


class StatisticalAnalyzer:
    def __init__(self):
        pass
