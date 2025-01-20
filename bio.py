import requests
import time

API_URL = "https://api-inference.huggingface.co/models/microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	while True:
		response = requests.post(API_URL, headers=headers, json=payload)
		if response.status_code == 200:
			return response.json()
		elif response.status_code == 503:  # Service Unavailable
			print("Model is loading, retrying in 5 seconds...")
			time.sleep(5)  # Wait before retrying
		else:
			print("Error:", response.json())
			break

output = query({
	"inputs": "[MASK] is a tyrosine kinase inhibitor.",
})
print(output)
