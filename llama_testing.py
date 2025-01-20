from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient

app = Flask(__name__)

client = InferenceClient(
    "mattshumer/Reflection-Llama-3.1-70B",
    token="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",
)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a world-class AI system, capable of complex reasoning and reflection. Reason through the query inside <thinking> tags, and then provide your final response inside <output> tags. If you detect that you made a mistake in your reasoning at any point, correct yourself inside <reflection> tags."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=500,
        temperature=0.7,
        top_p=0.95
    )
    
    # Collecting the response
    output_message = response.choices[0].delta.content
    return jsonify({"response": output_message})

if __name__ == '__main__':
    app.run(debug=True)