from PySide6.QtCore import QUrl, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QMenuBar, QSlider, QTextEdit, QVBoxLayout, QWidget


class MyMenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        self.file_menu = self.addMenu('&File')
        self.edit_menu = self.addMenu('&Edit')
        self.selection_menu = self.addMenu('&Selection')
        self.view_menu = self.addMenu('&View')


class MyWebView(QWebEngineView):
    def __init__(self, file_path):
        super().__init__()
        self.setFixedWidth(600)
        self.load(QUrl.fromLocalFile(file_path))


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QComboBox())
        layout.addWidget(QComboBox())

        self.setLayout(layout)
