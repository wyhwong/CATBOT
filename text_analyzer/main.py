import os
from utils.classification_inference import ClassificationInference

def main():
    pretrained = os.getenv("TEXT_INFERENCE_PRETRAINED")
    inference = ClassificationInference(pretrained)

if __name__ == "__main__":
    main()
