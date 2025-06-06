from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder(wake_words="jarvis")
    
    print('Say "Jarvis" to start recording.')
    print(recorder.text())