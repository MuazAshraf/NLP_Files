import anthropic
import os
from dotenv import load_dotenv
load_dotenv('.env')
ANTROPIC_API_KEY = os.getenv("ANTROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTROPIC_API_KEY)

response = client.beta.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
          "type": "computer_20241022",
          "name": "computer",
          "display_width_px": 1024,
          "display_height_px": 768,
          "display_number": 1,
        },
        {
          "type": "text_editor_20241022",
          "name": "str_replace_editor"
        },
        {
          "type": "bash_20241022",
          "name": "bash"
        }
    ],
    messages=[{"role": "user", "content": """take a screenshot and carefully evaluate if you have achieved the right outcome. Explicitly show your thinking: "I have evaluated step X..." If not correct, try again. Only when you confirm a step was executed correctly should you move on to the next one. then Open Google Chrome and navigate to https://www.chatgpt.com"""}],
    betas=["computer-use-2024-10-22"],
)
print(response)
