#Step: 1  Create a dataset for finetune
from datasets import load_dataset

dataset = load_dataset('json', data_files='deepseek_data.json')



#Step 2:Load the model and tokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "DeepSeek-R1-Distill-Qwen-1.5B"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

#Step 3: Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples['input'], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
#Example 
"""
Tokenization is the process of converting raw text into smaller units called tokens.
These tokens can be words, subwords, or even characters, depending on the tokenizer used. 
For example:

Input text: "What is the capital of France?"

Tokenized output: ["What", "is", "the", "capital", "of", "France", "?"]

"""


#Step 4: Define training arguments
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=4,
    num_train_epochs=3, #The number of times the model will iterate over the entire training dataset.
    logging_dir="./logs",
    logging_steps=10,
    save_steps=500,
    save_total_limit=2,
    evaluation_strategy="steps",
    eval_steps=500,
    learning_rate=5e-5,
    weight_decay=0.01,
    warmup_steps=500,
    fp16=True,
)

#Step 5: Initialize the trainer
from transformers import Trainer

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation'],  # Optional
)

#Step 6: Fine-tune the model
trainer.train()

#Structure of the fin-tuned-model directory
# fine-tuned-model/
# ├── pytorch_model.bin
# ├── config.json
# ├── tokenizer_config.json
# ├── vocab.json
# ├── merges.txt
# ├── special_tokens_map.json
# └── training_args.bin

#Step 7: Save the model
model.save_pretrained("./fine-tuned-model")
tokenizer.save_pretrained("./fine-tuned-model")

#Step 8: Evaluate the model (Optional)
eval_results = trainer.evaluate()
print(f"Evaluation results: {eval_results}")

#Step 9 Use the Finetune model
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("./fine-tuned-model")
tokenizer = AutoTokenizer.from_pretrained("./fine-tuned-model")

#Generate Text
input_text = "What is the capital of France?"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

