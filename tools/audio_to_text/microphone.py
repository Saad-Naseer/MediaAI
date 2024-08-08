import pyaudio

class MicrophoneStream:
    def __init__(self) -> None:
        
        # Setup PyAudio stream
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=2048  # Adjust chunk size if needed
        )
        self.stream.start_stream()
   
    def read(self):
        return self.stream.read(2048, exception_on_overflow=False)  # Match the chunk size

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()
        print("Stream stopped and resources released")