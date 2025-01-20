import requests
from flask import Flask, request, send_file, render_template
import requests
import io
import os
from PIL import Image


app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-v0.1"
headers = {"Authorization": "Bearer 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"}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        return prompt
    else:
        return render_template('home.html')

def query(payload):
    response = requests.post(API_URL, headers=headers, json={"inputs": payload})
    return response.content

if __name__ == '__main__':
    app.run(debug=True)