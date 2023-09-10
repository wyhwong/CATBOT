import numpy as np
from abc import ABC, abstractmethod
from p_tqdm import p_map, t_imap

from common_utils.common import load_yml
from common_utils.logger import get_logger

LOGGER = get_logger("text_analyzer/utils/text_scaper")


def _get_keywords() -> dict:
    """
    Get keywords.

    Args:
        None.
    Returns:
        Keywords (dict)."""
    return load_yml("./configs/text_analyzer/keywords.yml")


def _does_prompt_contain_keywords(prompt: str, keywords: list) -> str:
    """
    Check if prompt contains keywords.

    Args:
        prompt (str): Prompt to be checked.
        keywords (list): Keywords to be checked.
    Returns:
        Prompt (str) if prompt contains keywords, else None.
    """
    for keyword in keywords:
        if keyword.lower() in prompt.lower():
            return prompt


def _is_str(input) -> bool:
    """
    Check if input is string.

    Args:
        input (any): Input to be checked.
    Returns:
        True if input is string, else False. (bool)
    """
    if type(input) != str:
        return False
    return True


def _dummy_function(any_input: any) -> any:
    """
    Dummy function.

    Args:
        any_input (any): Any input.
    Returns:
        Any input. (any)
    """
    return any_input


class TextScraper(ABC):
    """
    Text Scraper.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize Text Scraper.

        Args:
            None.
        Returns:
            None.
        """
        self.keywords = _get_keywords()

    @abstractmethod
    def scrape(self, keywords: list) -> list:
        """
        Scrape text.
        """
        pass

    @abstractmethod
    def scrape_targets(self, targets: list) -> list:
        """
        Scrape text with targets.
        """
        pass

    def _filter_prompts_with_keywords(self, targets: list, prompts: list) -> list:
        """
        Filter prompts with keywords.

        Args:
            targets (list): Targets to filter the prompts.
            prompts (list): Prompts to be filtered.
        Returns:
            Prompts (list).
        """
        target_prompts = dict.fromkeys(targets, [])
        if not prompts:
            return target_prompts
        for target in targets:
            keywords = t_imap(_dummy_function, [self.keywords[target]] * len(prompts))
            prompts_with_keywords = p_map(
                _does_prompt_contain_keywords, np.array(prompts, dtype=str), keywords
            )
            target_prompts[target] = list(filter(None, prompts_with_keywords))
        return target_prompts
