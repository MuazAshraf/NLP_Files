from flask import Flask, request, send_file, render_template
import requests
import io
import os
from PIL import Image


app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": "Bearer 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"}
image_path = 'output_image.jpg'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        image_bytes = query(prompt)
        image = Image.open(io.BytesIO(image_bytes))
        image_path = 'output_image.jpg'
        image.save(image_path, 'JPEG')
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return render_template('home.html')

def query(payload):
    response = requests.post(API_URL, headers=headers, json={"inputs": payload})
    return response.content

if __name__ == '__main__':
    app.run(debug=True)








