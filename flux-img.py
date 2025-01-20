import requests
import io
from PIL import Image
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Check if the response is an image
    if response.headers['Content-Type'].startswith('image'):
        return response.content
    else:
        # Handle the case where the API does not return an image
        print("Error: API did not return an image.")
        print("Response:", response.text)
        return None

image_bytes = query({
    "inputs": "The world's largest black forest cake, the size of a building, surrounded by trees of the black forest",
})

if image_bytes:
    # Only proceed if an image was returned
    image = Image.open(io.BytesIO(image_bytes))
    image.save("cake.png")
else:
    # Handle the case where no image was returned
    print("No image to save.")