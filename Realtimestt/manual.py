###-------------------THIS IS MANUAL WAY TO RECORD AUDIO AND CONVERT TO TEXT-------------------###
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder()
    recorder.start()
    input("Press Enter to stop recording...")
    recorder.stop()
    print("Transcription: ", recorder.text())