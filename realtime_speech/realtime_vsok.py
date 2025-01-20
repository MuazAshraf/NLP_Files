import pyaudio
import vosk
import json
import queue
import threading
import time

# Audio configuration
CHANNELS = 1
FRAME_RATE = 16000
RECORD_SECONDS = 20
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2

# Initialize queues for messages and recordings
messages = queue.Queue()
recordings = queue.Queue()

# Initialize Vosk model
model = vosk.Model("C:\\Users\\MUAZ\\Downloads\\vosk-model-en-us-0.22") 
rec = vosk.KaldiRecognizer(model, FRAME_RATE)
rec.SetWords(True)

def record_microphone(chunk=1024):
    p = pyaudio.PyAudio()

    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=FRAME_RATE,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []

    print("Recording... Speak now!")

    while not messages.empty():
        data = stream.read(chunk)
        frames.append(data)
        if len(frames) >= (FRAME_RATE * RECORD_SECONDS) / chunk:
            recordings.put(frames.copy())
            frames = []

    stream.stop_stream()
    stream.close()
    p.terminate()

def speech_recognition():
    while not messages.empty():
        frames = recordings.get()
        rec.AcceptWaveform(b''.join(frames))
        result = rec.Result()
        text = json.loads(result)["text"]
        
        print("You said: " + text)
        time.sleep(1)

def start_recording():
    messages.put(True)
    record_thread = threading.Thread(target=record_microphone)
    record_thread.start()
    transcribe_thread = threading.Thread(target=speech_recognition)
    transcribe_thread.start()

def stop_recording():
    if not messages.empty():
        messages.get()
    print("Stopped recording.")

if __name__ == "__main__":
    try:
        start_recording()
        time.sleep(RECORD_SECONDS)  # Record for a specified duration
    except KeyboardInterrupt:
        stop_recording()