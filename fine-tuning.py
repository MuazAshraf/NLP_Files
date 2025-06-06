from datasets import load_dataset
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from tensorflow import keras
import numpy as np

# 1. Load and prepare dataset
dataset = load_dataset(path="medical")
dataset = dataset["train"]

# 2. Prepare labels first
medical_conditions = list(set(dataset["Medical Condition"]))
condition_mapping = {condition: idx for idx, condition in enumerate(medical_conditions)}

# 3. Tokenize with proper preprocessing
tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-cased")

def preprocess_function(examples):
    tokenized = tokenizer(examples["Name"], padding="max_length", truncation=True)
    tokenized["label"] = [condition_mapping[label] for label in examples["Medical Condition"]]
    return tokenized

# Process the dataset
processed_dataset = dataset.map(preprocess_function, batched=True)
processed_dataset = processed_dataset.remove_columns(dataset.column_names)
processed_dataset = processed_dataset.rename_column("label", "labels")

# Create a smaller subset and splits
small_dataset = processed_dataset.shuffle(seed=42).select(range(1000))
train_size = int(0.8 * len(small_dataset))
train_dataset = small_dataset.select(range(train_size))
val_dataset = small_dataset.select(range(train_size, len(small_dataset)))

# Load and compile model
model = TFAutoModelForSequenceClassification.from_pretrained(
    "google-bert/bert-base-cased", 
    num_labels=len(medical_conditions)
)

model.compile(
    optimizer=keras.optimizers.legacy.Adam(learning_rate=3e-5),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Convert to TF datasets
train_tf_dataset = model.prepare_tf_dataset(
    train_dataset, 
    batch_size=16, 
    shuffle=True
)

val_tf_dataset = model.prepare_tf_dataset(
    val_dataset,
    batch_size=16,
    shuffle=False
)

# Train
history = model.fit(
    train_tf_dataset,
    validation_data=val_tf_dataset,
    epochs=3
)