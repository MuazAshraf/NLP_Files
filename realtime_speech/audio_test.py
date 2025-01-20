import wave, os
import pyaudio
from faster_whisper import WhisperModel

def record_chunk(stream, file_path, chunk_length=1):
    frames = []
    for _ in range(0, int(16000 / 1024 * int(chunk_length))):  # Ensure chunk_length is an int
        data = stream.read(1024)
        frames.append(data)

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_chunk(model, file_path):
    return model.transcribe(file_path) 
def main():
    # Choose your model settings
    model_size = "medium.en"
    model = WhisperModel(device="cpu", compute_type="float32", model_size_or_path="medium.en")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(stream, chunk_file, chunk_length=1)  # Record audio chunk
            transcription_info = transcribe_chunk(model, chunk_file)

            # Extract the generator from transcription_info
            transcription_generator = transcription_info[0]  # Assuming the generator is the first item

            # Process each segment in real-time
            for segment in transcription_generator:
                print(segment.text)  # Print each segment's text
                accumulated_transcription += segment.text + " "  # Accumulate transcription

            os.remove(chunk_file)  # Remove the temporary chunk file

    except KeyboardInterrupt:
        print("Stopping...")
        # Write the accumulated transcription to the log file
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("LOG:", accumulated_transcription)

if __name__ == "__main__":
    main()
