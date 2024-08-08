from vosk import Model, KaldiRecognizer
import os

class vosk_recognizer:
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