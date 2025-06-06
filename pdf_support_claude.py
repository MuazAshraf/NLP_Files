from dotenv import load_dotenv
import os, base64, httpx
from anthropic import Anthropic
load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

client = Anthropic(api_key=ANTHROPIC_API_KEY)
pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode('utf-8')
response = client.beta.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    betas = ["pdfs-2024-09-25"],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    },
                    "cache_control": {"type": "ephemeral"}
                },
                {
                    "type": "text",
                    "text": "What are the key findings in this document?"
                }
            ]
        }
    ],
)

print(response.content)