from openai import OpenAI
client = OpenAI(api_key='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')

audio_file = open("test.mp3", "rb")
translation = client.audio.translations.create(
  model="whisper-1", 
  file=audio_file,
  
)
print(translation.text)