import pyaudio
import numpy as np
from speechbrain.inference.ASR import StreamingASR
from speechbrain.utils.dynamic_chunk_training import DynChunkTrainConfig

# Initialize the ASR model
asr_model = StreamingASR.from_hparams(
    source="speechbrain/asr-streaming-conformer-librispeech",
    savedir="pretrained_models/asr-streaming-conformer-librispeech"
)

# Audio configuration
CHUNK = 1024  # Number of audio samples per frame
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Start recording
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Recording... Speak now!")

try:
    while True:
        # Read audio data from the stream
        audio_data = stream.read(CHUNK)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Transcribe the audio chunk using streaming method
        # Convert audio_array to bytes
        audio_bytes = audio_array.tobytes()
        transcription = asr_model.transcribe_file_streaming(audio_bytes, DynChunkTrainConfig(24, 4))

        # Print the transcription
        for text_chunk in transcription:
            print(text_chunk)

except KeyboardInterrupt:
    print("Stopped recording.")

finally:
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
