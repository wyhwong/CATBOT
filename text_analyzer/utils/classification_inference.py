import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

class ClassificationInference:
    def __init__(self, pretrained: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForSequenceClassification.from_pretrained(pretrained)
