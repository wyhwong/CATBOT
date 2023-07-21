import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from common_utils.logger import get_logger
from common_utils.common import load_yml

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
LOGGER = get_logger("text_analyzer/utils/classification_inference")


def _get_class_to_label():
    return load_yml("./configs/text_analyzer/class_to_label.yml")


class ClassificationInference:
    def __init__(self, pretrained: str) -> None:
        LOGGER.debug("Initializing text classification inference...")
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained)
        self.model.to(DEVICE)
        self.labels = _get_class_to_label()
        LOGGER.info("Initialized text classification inference.")

    def __call__(self, prompt):
        LOGGER.info(f"Input: {prompt=}")
        model_input = self.tokenizer(prompt, padding=True, truncation=True, max_length=512, return_tensors="pt")
        model_output = self.model(model_input["input_ids"], attention_mask=model_input["attention_mask"])
        model_output = nn.functional.softmax(model_output.logits, dim=-1).detach().numpy()[0]
        LOGGER.info(f"Output: {model_output=}")
        return model_output

    def get_score(self, prompt: str) -> float:
        target_score = 0
        class_scores = self.__call__(prompt)
        for idx, score in enumerate(class_scores):
            target_score += self.labels[idx]["weights"] * score
        LOGGER.info(f"{prompt=}, {score=}")
        return target_score

    def get_prompts_scores(self, prompts: list) -> float:
        LOGGER.info(f"Received number of prompts: {len(prompts)}")
        target_score = 0
        for prompt in prompts:
            class_scores = self.__call__(prompt)
            for idx, score in enumerate(class_scores):
                target_score += (self.labels[idx]["weights"] * score) / len(prompts)
        return target_score
