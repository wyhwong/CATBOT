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
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained)
        self.model.to(DEVICE)
        self.labels = _get_class_to_label()

    def __call__(self, prompt: str) -> str:
        model_input = self.tokenizer(prompt,
                                     padding=True,
                                     truncation=True,
                                     max_length=512,
                                     return_tensors="pt")
        model_output = self.model(model_input["input_ids"], attention_mask=model_input["attention_mask"])
        class_scores = nn.functional.softmax(model_output.logits, dim=-1).detach().numpy()[0]
        weighted_score = 0
        for idx, score in enumerate(class_scores):
            weighted_score += self.labels[idx]["weights"] * score
        return weighted_score
