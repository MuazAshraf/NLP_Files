from pathlib import Path
from openai import OpenAI
client = OpenAI(api_key = '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')

speech_file_path = Path(__file__).parent / "speech2.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="onyx",
  input="""Remember, the future of creativity is in your hands, and with tools like these, there are no limits to what you can create. Until next time, keep innovating!. I will drop the GitHub code Link In Description below"""
)

response.stream_to_file(speech_file_path)