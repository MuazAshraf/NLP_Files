import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import sounddevice as sd
import numpy as np

# Parameters
sample_rate = 16000  # Whisper expects 16 kHz sample rate
channels = 1         # Mono audio
duration = 5         # Duration of recording in seconds

print("Starting the script...")

# Force model to load in CPU mode
device = "cpu"
torch_dtype = torch.float32

try:
    # Load the model and processor
    print("Loading model and processor...")
    model_id = "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)

    # Create a pipeline for automatic speech recognition with chunking and timestamping enabled
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=60,  # Chunk length for long audio files
        torch_dtype=torch_dtype,
        device=device
    )

    print("Model and processor loaded successfully!")

    # Function to record audio
    def record_audio():
        print(f"Recording for {duration} seconds...")

        # Record audio for the specified duration
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
        sd.wait()  # Wait for the recording to finish

        print("Recording complete!")
        return np.reshape(audio_data, (-1,)).astype(np.float32)  # Flatten the audio array

    # Function to transcribe audio using Whisper with timestamps
    def transcribe_audio(audio_data):
        print("Transcribing audio with timestamps...")
        

        # Pass the audio data to the Whisper pipeline with timestamping enabled
        result = pipe(audio_data, return_timestamps="sentence", generate_kwargs={"language": "english"})  # or "sentence" for sentence-level timestamps
        
        # Output the transcription and timestamps
        for chunk in result["chunks"]:
            print(f"Word: {chunk['text']} | Start: {chunk['timestamp'][0]} | End: {chunk['timestamp'][1]}")

    # Step 1: Record the audio
    recorded_audio = record_audio()

    # Step 2: Transcribe the recorded audio with timestamps
    transcribe_audio(recorded_audio)

except Exception as e:
    print(f"Error occurred: {e}")
