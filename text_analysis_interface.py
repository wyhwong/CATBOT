import torch
from transformers import BertForSequenceClassification, BertTokenizer

# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load the trained model from file
loaded_model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)


# Define some example financial text
examples = [
    'The stock market is doing bad today!',
    'Cash flow not enough.',
    'company bankruptcy.',
   
]

# Define the sentiment labels
sentiment_labels = ['Positive', 'Neutral', 'Negative']

# Make predictions on the example text
loaded_model.eval()
with torch.no_grad():
    for example in examples:
        inputs = tokenizer.encode_plus(
            example,
            add_special_tokens=True,
            max_length=512,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']
        output = loaded_model(input_ids, attention_mask=attention_mask)
        logits = output[0]
        softmax = torch.nn.functional.softmax(logits, dim=1)
        prediction = torch.argmax(softmax, dim=1)
        print(f'Example: {example}')
        print(f'Sentiment: {sentiment_labels[prediction.item()]}')

