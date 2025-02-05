from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


speech_file_path = Path(__file__).parent / "speech2.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="onyx",
  input="""Remember, the future of creativity is in your hands, and with tools like these, there are no limits to what you can create. Until next time, keep innovating!. I will drop the GitHub code Link In Description below"""
)

response.stream_to_file(speech_file_path)
