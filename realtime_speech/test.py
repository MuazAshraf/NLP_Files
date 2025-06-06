import speech_recognition as sr
import pyaudio

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to transcribe audio in real-time
def transcribe_audio():
    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Recording... Speak now!")

        # Continuously listen for audio
        while True:
            try:
                # Listen for audio
                audio_data = recognizer.listen(source)
                print("Transcribing...")
                
                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio_data)
                print("You said: " + text)
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

# Start the transcription
if __name__ == "__main__":
    transcribe_audio()