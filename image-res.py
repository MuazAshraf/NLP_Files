from flask import Flask, request, send_file
from PIL import Image
import torch
import numpy as np
from transformers import AutoImageProcessor, Swin2SRForImageSuperResolution
import io

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model and processor
processor = AutoImageProcessor.from_pretrained("caidas/swin2SR-classical-sr-x2-64")
model = Swin2SRForImageSuperResolution.from_pretrained("caidas/swin2SR-classical-sr-x2-64")

def enhance(image):
    # Prepare the image for the model
    inputs = processor(image, return_tensors="pt")

    # Forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Post-process the output
    output = outputs.reconstruction.data.squeeze().float().cpu().clamp_(0, 1).numpy()
    output = np.moveaxis(output, source=0, destination=-1)
    output = (output * 255.0).round().astype(np.uint8)  # float32 to uint8

    return Image.fromarray(output)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            image = Image.open(file.stream)
            enhanced_image = enhance(image)
            img_io = io.BytesIO()
            enhanced_image.save(img_io, format='JPEG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')

    return '''
    <!doctype html>
    <title>Image Super-Resolution</title>
    <h1>Upload a low-resolution image</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
