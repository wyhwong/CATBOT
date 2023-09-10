import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from common_utils.logger import get_logger
from common_utils.common import load_yml

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
LOGGER = get_logger("text_analyzer/utils/classification_inference")


def _get_class_to_label():
    """
    Get class to label mapping.

    Args:
        None.
    Returns:
        Class to label mapping (dict).
    """
    return load_yml("./configs/text_analyzer/class_to_label.yml")


class ClassificationInference:
    """
    Text classification inference.
    """

    def __init__(self, pretrained: str) -> None:
        """
        Initialize text classification inference.

        Args:
            pretrained (str): Pretrained model.
        Returns:
            None.
        """
        LOGGER.debug("Initializing text classification inference...")
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained)
        self.model.to(DEVICE)
        self.labels = _get_class_to_label()
        LOGGER.info("Initialized text classification inference.")

    def __call__(self, prompt):
        """
        Call text classification inference.

        Args:
            prompt (str): Prompt to be classified.
        Returns:
            Class scores (list).
        """
        LOGGER.info(f"Input: {prompt=}")
        model_input = self.tokenizer(
            prompt, padding=True, truncation=True, max_length=512, return_tensors="pt"
        )
        model_output = self.model(
            model_input["input_ids"], attention_mask=model_input["attention_mask"]
        )
        model_output = (
            nn.functional.softmax(model_output.logits, dim=-1).detach().numpy()[0]
        )
        LOGGER.info(f"Output: {model_output=}")
        return model_output

    def get_score(self, prompt: str) -> float:
        """
        Get score of the prompt.

        Args:
            prompt (str): Prompt to be classified.
        Returns:
            Score of the prompt (float).
        """
        target_score = 0
        class_scores = self.__call__(prompt)
        for idx, score in enumerate(class_scores):
            target_score += self.labels[idx]["weights"] * score
        LOGGER.info(f"{prompt=}, {score=}")
        return target_score

    def get_prompts_scores(self, prompts: list) -> float:
        """
        Get score of the prompts.

        Args:
            prompts (list): Prompts to be classified.
        Returns:
            Score of the prompts (float).
        """
        LOGGER.info(f"Received number of prompts: {len(prompts)}")
        target_score = 0
        for prompt in prompts:
            class_scores = self.__call__(prompt)
            for idx, score in enumerate(class_scores):
                target_score += (self.labels[idx]["weights"] * score) / len(prompts)
        return target_score
