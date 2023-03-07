import pandas as pd
import numpy as np
from transformers import BertTokenizer, TFAutoModelForSequenceClassification

# Load the pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = TFAutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)

# Load the financial text data
df = pd.read_csv("financial_data.csv")


# Tokenize the financial text data
def tokenize_text(text):
    # Add special tokens
    encoded_text = tokenizer.encode_plus(
        text,
        max_length=512,
        add_special_tokens=True,
        return_token_type_ids=False,
        padding="max_length",
        return_attention_mask=True,
        return_tensors="tf",
        truncation=True,
    )
    return encoded_text


df["input_ids"] = df["text"].apply(lambda x: tokenize_text(x)["input_ids"])
df["attention_mask"] = df["text"].apply(lambda x: tokenize_text(x)["attention_mask"])

# Split the labeled data into training, validation, and test sets
train_df = df[:800]
val_df = df[800:900]
test_df = df[900:]

# Convert the data to TensorFlow tensors and create TensorFlow datasets
train_inputs = np.array(train_df["input_ids"].tolist())
train_masks = np.array(train_df["attention_mask"].tolist())
train_labels = np.array(train_df["label"].tolist())
train_dataset = tf.data.Dataset.from_tensor_slices((train_inputs, train_masks, train_labels)).batch(32)

val_inputs = np.array(val_df["input_ids"].tolist())
val_masks = np.array(val_df["attention_mask"].tolist())
val_labels = np.array(val_df["label"].tolist())
val_dataset = tf.data.Dataset.from_tensor_slices((val_inputs, val_masks, val_labels)).batch(32)

test_inputs = np.array(test_df["input_ids"].tolist())
test_masks = np.array(test_df["attention_mask"].tolist())
test_labels = np.array(test_df["label"].tolist())
test_dataset = tf.data.Dataset.from_tensor_slices((test_inputs, test_masks, test_labels)).batch(32)

# Train the BERT model
optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5)
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
epochs = 10

for epoch in range(epochs):
    model.train()
    for batch in train_dataset:
        inputs, masks, labels = batch
        # Forward pass
        with tf.GradientTape() as tape:
            outputs = model(inputs, attention_mask=masks, training=True)
            loss = loss_fn(labels, outputs.logits)
        # Backward pass
        grads = tape.gradient(loss, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))
    # Evaluate the model on the validation set
    model.eval()
    val_preds = []
    val_labels = []
    for batch in val_dataset:
        inputs, masks, labels = batch
        outputs = model(inputs, attention_mask=masks)
        val_preds.extend(np.argmax(outputs.logits.numpy(), axis=1).tolist())
        val_labels.extend(labels.numpy().tolist())
    # Print validation metrics
    print(
        "Epoch:",
        epoch + 1,
        "Val accuracy:",
        accuracy_score(val_labels, val_preds),
        "Val precision:",
        precision_score(val_labels, val_preds, average="weighted"),
        "Val recall:",
        recall_score(val_labels, val_preds, average="weighted"),
        "Val F1 score:",
        f1_score(val_labels, val_preds, average="weighted"),
        "Val confusion matrix:",
        confusion_matrix(val_labels, val_preds),
    )

# Evaluate the model on the test set
test_preds = []
test_labels = []
for batch in test_dataset:
    inputs, masks, labels = batch
    outputs = model(inputs, attention_mask=masks)
    test_preds.extend(np.argmax(outputs.logits.numpy(), axis=1).tolist())
    test_labels.extend(labels.numpy().tolist())

# Print test metrics
print("Test accuracy:", accuracy_score(test_labels, test_preds))
print("Test precision:", precision_score(test_labels, test_preds, average="weighted"))
print("Test recall:", recall_score(test_labels, test_preds, average="weighted"))
print("Test F1 score:", f1_score(test_labels, test_preds, average="weighted"))
print("Test confusion matrix:", confusion_matrix(test_labels, test_preds))
