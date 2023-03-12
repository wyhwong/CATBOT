import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from common_utils.logger import get_logger
from common_utils.common import read_content_from_yml

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
LOGGER = get_logger(logger_name="Utils | Classification Inference")


def _get_class_to_label():
    return read_content_from_yml(path="./configs/class_to_label.yml")


class ClassificationInference:
    def __init__(self, pretrained: str) -> None:
        LOGGER.info("Initializing text classification inference...")
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained)
        self.model.to(DEVICE)
        self.labels = _get_class_to_label()
        LOGGER.info("Initialized text classification inference.")

    def __call__(self, prompt):
        LOGGER.debug(f"Input: {prompt=}")
        model_input = self.tokenizer(prompt, padding=True, truncation=True, max_length=512, return_tensors="pt")
        model_output = self.model(model_input["input_ids"], attention_mask=model_input["attention_mask"])
        model_output = nn.functional.softmax(model_output.logits, dim=-1).detach().numpy()[0]
        LOGGER.debug(f"Output: {model_output=}")
        return model_output

    def get_score(self, prompts: list) -> str:
        LOGGER.info(f"Received number of prompts: {len(prompts)}")
        target_score = 0
        for prompt in prompts:
            class_scores = self.__call__(prompt)
            for idx, score in enumerate(class_scores):
                target_score += (self.labels[idx]["weights"] * score) / len(prompts)
        return target_score
