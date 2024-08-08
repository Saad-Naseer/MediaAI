import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QFileDialog, QLabel, QWidget, QGridLayout
from PyQt6.QtWidgets import QComboBox, QSpacerItem, QSizePolicy
#from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from tools.audio_to_text.audio_to_text import SpeechRecognizer
from threading import Thread

class MediaAiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MediaAI")
        #self.setWindowIcon(QIcon("../../icon/icon.png"))
        self.setGeometry(100, 100, 600, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)
        
        self.result_layout = QGridLayout()
        self.layout.addLayout(self.result_layout, 0 , 0)
        
        self.result_label = QLabel("Result:")
        self.result_layout.addWidget(self.result_label, 0, 0)

        self.text_edit = QTextEdit(self)
        self.result_layout.addWidget(self.text_edit, 1, 0)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.status_label = QLabel('', self)
        self.result_layout.addWidget(self.status_label, 2, 0)
        
        self.btns_layout = QGridLayout()
        self.layout.addLayout(self.btns_layout, 0, 1)

        self.record_button = QPushButton('Record from Mic', self)
        self.record_button.clicked.connect(self.mic_to_text)
        self.btns_layout.addWidget(self.record_button, 3, 0)
        
        self.upload_button = QPushButton('Upload Audio File', self)
        self.upload_button.clicked.connect(self.upload_file)
        self.btns_layout.addWidget(self.upload_button, 4, 0)
        
        self.create_language_combobox()
        self.create_model_combobox()
        self.create_engine_combobox()
        self.create_out_file_combobox()
        self.generate_file_button = QPushButton('Generate File', self)
        self.generate_file_button.clicked.connect(self.generate_file)
        self.btns_layout.addWidget(self.generate_file_button, 6, 0)
        # Create a spacer item to push the layout content up
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.btns_layout.addItem(self.spacer, 7, 0)  # Place the spacer at the top
        self.layout.setColumnStretch(3,0)
        self.show()
    
    def create_language_combobox(self):
        self.language_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.language_combobox_layout,0 , 0)

        self.language_combobox = QComboBox()
        self.language_combobox_label = QLabel("Select Language:")
        self.language_combobox.addItems([
            "English (US) - en",
            "Spanish - es", "French - fr",
            "German - de"
        ])
        self.language_combobox.currentIndexChanged.connect(self.change_language)
        self.language_combobox_layout.addWidget(self.language_combobox_label, 0, 0)
        self.language_combobox_layout.addWidget(self.language_combobox, 1, 0)
        self.change_language()
        
    
    def change_language(self):
        lang_code = self.language_combobox.currentText().split(" - ")[1]
        self.language = lang_code
    
    def create_engine_combobox(self):
        self.engine_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.engine_combobox_layout, 1, 0)
        self.engine_combobox = QComboBox()
        self.engine_combobox_label = QLabel("Select Engine:")
        self.engine_combobox.addItems([
            "whisper",
            "vosk",
        ])
        self.engine_combobox.currentIndexChanged.connect(self.change_engine)
        self.engine_combobox_layout.addWidget(self.engine_combobox_label, 0, 0)
        self.engine_combobox_layout.addWidget(self.engine_combobox, 1, 0)
        self.change_engine()
    
    def change_engine(self):
        self.engine = self.engine_combobox.currentText()
        self.model_combobox.clear()
        if self.engine == "whisper":
            self.model_combobox.addItems([
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "tiny.en",
            "base.en",
            "small.en",
            "medium.en"
            ])
        if self.engine == "vosk":
            self.model_combobox.addItems([
            "fast",
            ])

    def create_model_combobox(self):
        self.model_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.model_combobox_layout, 2, 0)
        self.model_combobox = QComboBox()
        self.model_combobox_label = QLabel("Select Model:")
       
        self.model_combobox.currentIndexChanged.connect(self.change_model)
        self.model_combobox_layout.addWidget(self.model_combobox_label, 0, 0)
        self.model_combobox_layout.addWidget(self.model_combobox, 1, 0)
        self.change_model()
    
    def change_model(self):
        self.model = self.model_combobox.currentText()

    def create_out_file_combobox(self):
        self.out_file_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.out_file_combobox_layout, 5, 0)
        self.out_file_combobox = QComboBox()
        self.out_file_combobox_label = QLabel("Select Output File Type:")
        self.out_file_combobox.addItems([".txt", ".srt", ".vtt"])
        self.out_file_combobox.currentIndexChanged.connect(self.change_out_file_type)
        self.out_file_combobox_layout.addWidget(self.out_file_combobox_label, 0, 0)
        self.out_file_combobox_layout.addWidget(self.out_file_combobox, 1, 0)
        self.change_out_file_type()
    
    def change_out_file_type(self):
        if self.text !=None:
           self.update_file_type()

    def update_file_type(self):
        if self.out_file_combobox.currentText()==".txt":
            txt = self.speech_recognizer.dict_to_text(self.text)
            self.text_edit.setText(txt)
        elif self.out_file_combobox.currentText()==".srt":
            srt = self.speech_recognizer.dict_to_srt(self.text)
            self.text_edit.setText(srt)
        elif self.out_file_combobox.currentText()==".vtt":
            vtt = self.speech_recognizer.dict_to_vtt(self.text)
            self.text_edit.setText(vtt)

    def mic_to_text(self):
        self.speech_recognizer = SpeechRecognizer(tool="mic", language=self.language, engine=self.engine, model=self.model)
        self.speech_recognizer.status_update.connect(self.status_update)
        self.speech_recognizer.text_update.connect(self.text_update)
        self.speech_recognizer.start()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.mp3)")
        if file_path:
            self.speech_recognizer= SpeechRecognizer(tool="file", language=self.language, file_path=file_path, engine = self.engine, model = self.model)
            self.speech_recognizer.status_update.connect(self.status_update)
            self.speech_recognizer.text_update.connect(self.text_update)
            self.speech_recognizer.start()

    def generate_file(self):
        # Prompt the user to select a folder
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if selected_folder:
            # Combine the selected folder path with the filename
            file_path = selected_folder + "/out" + self.out_file_combobox.currentText()
            try:
                # Write the contents of the text edit to the file
                with open(file_path, "w") as file:
                    file.write(self.text_edit.toPlainText())
                    self.status_update("File saved :"+ file_path)

            except PermissionError as e:
                self.status_update(str(e))

    def status_update(self, status):
        self.status_label.setText(status)

    def text_update(self, text):
        self.text = text
        self.update_file_type()


def main():
    app = QApplication(sys.argv)
    ex = MediaAiApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()