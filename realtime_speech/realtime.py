from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import sounddevice as sd
import numpy as np
import torch
# tokenizer = Wav2Vec2Tokenizer.from_pretrained('facebook/wav2vec2-base-960h')
model_id = "openai/whisper-large-v3"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

def record_audio(duration):
    fs = 16000  # Sample rate
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    return audio.flatten()

def transcribe_audio(audio):
    # Process the audio input
    inputs = processor(audio, sampling_rate=16000, return_tensors='pt')
    
    # Print the structure of inputs for debugging
    print("Inputs structure:", inputs)

    # Check if 'input_features' exists in the inputs
    if 'input_features' in inputs:
        input_features = inputs['input_features'].to(device)
    else:
        raise ValueError("The processed inputs do not contain 'input_features'. Please check the processor configuration.")

    with torch.no_grad():
        # Get the model's logits
        # Add decoder_input_ids to the model call
        logits = model(input_features, decoder_input_ids=torch.zeros(input_features.shape[0], 1).long().to(device)).logits
    
    # Get the predicted IDs
    predicted_ids = torch.argmax(logits, dim=-1)
    
    # Decode the predicted IDs to get the transcription
    transcription = processor.batch_decode(predicted_ids)
    return transcription

while True:
    audio = record_audio(5)  # Record for 5 seconds
    transcription = transcribe_audio(audio)
    print(transcription)
