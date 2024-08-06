import speech_recognition as sr
from threading import Thread
from PyQt6.QtCore import pyqtSignal, QObject

class SpeechRecognizer(QObject, Thread):
    status_update = pyqtSignal(str)
    text_update = pyqtSignal(dict)
    
    def __init__(self, tool=None, language="en-EN", file_path=None, model=None):
        QObject.__init__(self)
        Thread.__init__(self)
        self.recognizer = sr.Recognizer()
        self.tool = tool
        self.language = language
        self.file_path = file_path
        self.model = model

    def run(self):
        if self.tool == "mic":
            self.mic_to_text(language=self.language, model=self.model)
        elif self.tool == "file":
            if self.file_path:
                self.file_to_text(file_path=self.file_path, language=self.language, model=self.model)
        
    def set_status(self, status: str):
         print("emit")
         self.status_update.emit(status)

    def set_text(self, text):
         self.text_update.emit(text)


    def dict_to_text(self, data):
        text = data['text']
        return text

    def format_time(self, seconds, separator=','):
        """Convert seconds to SRT or VTT time format."""
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{millis:03}"

    def dict_to_srt(self, data):
        """Convert a dictionary with subtitle data to an SRT formatted string."""
        srt = ""
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'], ',')
            end = self.format_time(segment['end'], ',')
            text = segment['text'].strip()
            
            srt += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
        
        return srt
    
    def dict_to_vtt(self, data):
        """Convert a dictionary with subtitle data to a VTT formatted string."""
        vtt = "WEBVTT\n\n"
        for i, segment in enumerate(data['segments']):
            start = self.format_time(segment['start'], '.')
            end = self.format_time(segment['end'], '.')
            text = segment['text'].strip()
            
            vtt += f"{start} --> {end}\n{text}\n\n"
        
        return vtt
    
    def mic_to_text(self, language, model):
        with sr.Microphone() as source:
            self.set_status("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
            self.set_status("Listening... Speak into the mic")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                self.set_status("Processing...")
                #text = self.recognizer.recognize_google(audio, language=language)
                text = self.recognizer.recognize_whisper(audio_data=audio, language=language, show_dict=True, model=model)
                self.set_status("Done")
                self.set_text(text)

            
            except sr.WaitTimeoutError:
                self.set_status("No audio detected from mic")
            except sr.UnknownValueError:
                self.set_status("Google could not understand the audio")
            except sr.RequestError as e:
               self.set_status(f"Request to Google service failed: {e}")
            except Exception as e:
                 self.set_status(f"An error occurred: {e}")

    def file_to_text(self, file_path, language, model):
        with sr.AudioFile(file_path) as source:
            self.set_status("Processing...")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                #text = self.recognizer.recognize_google(audio, language=self.language, show_all=True)
                text = self.recognizer.recognize_whisper(audio, language=language, show_dict=True, model=model)
                 #with open("audio_file_to_text.txt", "w") as file:
                #    file.write(text)
                self.set_status("Done")
                self.set_text(text)
                #srt_output = self.dict_to_srt(text)
                #print("srt: ", srt_output)
            except sr.UnknownValueError:
                self.set_status("Google could not understand the audio")
            except sr.RequestError as e:
                self.set_status(f"Request to Google service failed: {e}")
            except Exception as e:
                self.set_status(f"An error occurred: {e}")
