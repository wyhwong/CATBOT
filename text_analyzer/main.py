#!/usr/bin/env python3
import os

from utils.classification_inference import ClassificationInference
from common_utils.logger import get_logger

LOGGER = get_logger(logger_name="Main | Text Analyzer")

def main():
    pretrained = os.getenv("TEXT_INFERENCE_PRETRAINED")
    inference = ClassificationInference(pretrained=pretrained)
    text = "The USD rallied by 10% last night"
    results = inference(prompt=text)
    print(results)

if __name__ == "__main__":
    main()
