from flask import Flask, request, jsonify
import os
import time
import requests
from dotenv import load_dotenv
import logging
import base64

load_dotenv()
BFL_API_KEY = os.getenv("BFL_API_KEY")

app = Flask(__name__)
def send_image_to_api(image_bytes, ssa, site_id):
    api_url = "https://mojomosaic.xyz/api/v1/langchain/pdf-upload-gallery"
    token = "be086981-630f-4a1a-8c47-712a9e128e55"
    
    # Save the image temporarily to disk as the API expects a file path
    file_path = "temp_image.png"
    with open(file_path, 'wb') as file:
        file.write(image_bytes)

    # Prepare the file and data payload
    with open(file_path, 'rb') as file:
        files = {'files': (os.path.basename(file_path), file, 'image/png')}
        data = {
            'ssa': ssa,
            'site_id': site_id
        }

        response = requests.post(api_url, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, files=files, data=data)
        logging.info(f"Sending POST request to: {api_url} with filename: {os.path.basename(file_path)}")
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Body: {response.text}")
    
    # Clean up the temporary file
    os.remove(file_path)
    
    return response

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    ssa = data.get('ssa')
    site_id = data.get('site_id')
    # Check required fields
    if not prompt or not ssa:
        print("Missing required fields in the request.")
        return jsonify({"error": "prompt, SSA, and site ID are required"}), 400

    # Step 1: Create an image
    response = requests.post(
        'https://api.bfl.ml/v1/image',
        headers={
            'accept': 'application/json',
            'x-key': BFL_API_KEY,
            'Content-Type': 'application/json',
        },
        json={
            'prompt': prompt,
            'width': 1024,  # Fixed width
            'height': 1024,  # Fixed height
        },
    )

    # Check if the request was successful
    if response.status_code == 200:
        request_data = response.json()
        request_id = request_data["id"]
    else:
        return jsonify({"error": f"Error: {response.status_code} - {response.text}"}), response.status_code

    # Step 2: Poll for the result
    while True:
        time.sleep(0.5)  # Wait for half a second before polling again
        result_response = requests.get(
            'https://api.bfl.ml/v1/get_result',
            headers={
                'accept': 'application/json',
                'x-key': BFL_API_KEY,
            },
            params={
                'id': request_id,
            },
        )

        
        # Check if the result request was successful
        if result_response.status_code == 200:
            result = result_response.json()
            if result["status"] == "Ready":
                image_url = result['result']['sample']  # Assuming this is the correct URL
                print(f"Image URL: {image_url}")

                # Download the image
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Send the image to the external API
                    response = send_image_to_api(image_response.content, ssa, site_id)
                    return jsonify({"status": "Image generated and sent", "api_response": response.text}), 200
                else:
                    return jsonify({"error": f"Failed to download image: {image_response.status_code} - {image_response.text}"}), 500
            else:
                print(f"Status: {result['status']}")
        else:
            return jsonify({"error": f"Error: {result_response.status_code} - {result_response.text}"}), result_response.status_code

if __name__ == '__main__':
    app.run(debug=True)