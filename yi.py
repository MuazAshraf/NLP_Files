from huggingface_hub import InferenceClient

client = InferenceClient(
    "01-ai/Yi-1.5-34B-Chat",
    token="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",
)

for message in client.chat_completion(
	messages=[{"role": "user", "content": "What is the capital of France?"}],
	max_tokens=500,
	stream=True,
):
    print(message.choices[0].delta.content, end="")
