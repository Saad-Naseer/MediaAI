import pyaudio
import json
from vosk import Model, KaldiRecognizer
import os
class vosk_recognition:
    def __init__(self) -> None:
        # Load Vosk model
        model_path = "model\\vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please download the model and unpack it.")
        model = Model(model_path)
        self.recognizer = KaldiRecognizer(model, 16000)
    
    def data(self, data):
        return self.recognizer.AcceptWaveform(data)
    
    def get_result(self):
        return self.recognizer.Result()
    
    def get_partial_result(self):
        return self.recognizer.PartialResult()

class MicrphoneStreaming:
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


if __name__=="__main__":
    mic = MicrphoneStreaming()
    vosk = vosk_recognition()
    while True:
        if vosk.data(mic.read()):
            result = json.loads(vosk.get_result())
            print(f"Full: {result.get('text', '')}")
        else:
            partial_result = json.loads(vosk.get_partial_result())
            print(f"Partial: {partial_result.get('partial', '')}")

     