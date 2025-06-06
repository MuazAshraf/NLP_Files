from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, base64, httpx
from anthropic import Anthropic
app = Flask(__name__)
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = Anthropic(api_key=ANTHROPIC_API_KEY)
# Store conversation history
conversations = {}
def process_pdf(pdf_data):
   """Convert PDF data to base64"""
   return base64.standard_b64encode(pdf_data).decode('utf-8')
@app.route('/chat', methods=['POST'])
def chat():
   try:
       data = request.json
       conversation_id = data.get('conversation_id', 'default')
       query = data.get('query')
       pdf_url = data.get('pdf_url')
       pdf_file = request.files.get('pdf_file')
       if not query:
           return jsonify({"error": "Query is required"}), 400
        # Get PDF content either from URL or uploaded file
       if pdf_url:
           pdf_data = httpx.get(pdf_url).content
       elif pdf_file:
           pdf_data = pdf_file.read()
       else:
           return jsonify({"error": "Either pdf_url or pdf_file is required"}), 400
        # Convert PDF to base64
       pdf_base64 = process_pdf(pdf_data)
        # Get conversation history
       if conversation_id not in conversations:
           conversations[conversation_id] = []
        # Prepare messages with conversation history
       messages = conversations[conversation_id] + [
           {
               "role": "user",
               "content": [
                   {
                       "type": "document",
                       "source": {
                           "type": "base64",
                           "media_type": "application/pdf",
                           "data": pdf_base64
                       },
                       "cache_control": {"type": "ephemeral"}
                   },
                   {
                       "type": "text",
                       "text": query
                   }
               ]
           }
       ]
        # Get response from Claude
       response = client.beta.messages.create(
           model="claude-3-5-sonnet-20240620",
           max_tokens=1024,
           betas=["pdfs-2024-09-25"],
           messages=messages
       )
        # Update conversation history
       conversations[conversation_id].extend([
           messages[-1],  # Add user message
           {"role": "assistant", "content": response.content}  # Add assistant response
       ])
       return jsonify({
           "conversation_id": conversation_id,
           "response": response.content
       })
   except Exception as e:
       return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
   app.run(debug=True)