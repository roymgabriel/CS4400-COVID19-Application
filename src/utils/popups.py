from PyQt5.QtWidgets import *


class Error(QDialog):
    def __init__(self, message):
        super(Error, self).__init__()
        self.setWindowTitle('Error')
        self.setMinimumWidth(300)

        self.error_msg = QLabel(message)
        self.go_back = QPushButton("Close")

        error_display = QVBoxLayout(self)
        error_display.addWidget(self.error_msg)
        error_display.addWidget(self.go_back)

        self.go_back.clicked.connect(self.close)


class Message(QDialog):
    def __init__(self, message):
        super(Message, self).__init__()
        self.setWindowTitle('Message')
        self.setMinimumWidth(300)

        self.error_msg = QLabel(message)
        self.go_back = QPushButton("Close")

        error_display = QVBoxLayout(self)
        error_display.addWidget(self.error_msg)
        error_display.addWidget(self.go_back)

        self.go_back.clicked.connect(self.close)