from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Using with_streaming_response as recommended
speech_file_path = Path("output2.mp3")
with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="echo",
    #input="""َٱلۡوَٰلِدَٰتُ يُرۡضِعۡنَ أَوۡلَٰدَهُنَّ حَوۡلَيۡنِ كَامِلَيۡنِۖ""",
    input = """مائیں اپنے بچوں کو پورے دو سال دودھ پلا سکتی ہیں""",
    response_format="mp3"
) as response:
    response.stream_to_file(speech_file_path)