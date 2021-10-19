from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QStyleFactory, QToolBar, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PZSP2")
        self.setStyleSheet('MainWindow {background-color:#7d7d7d}')

        self.setup_menubar()
        self.setup_webview(file_path)
        temp_widget = QLabel("temp")
        temp_widget.setMinimumWidth(300)

        layout = QHBoxLayout()
        layout.addWidget(temp_widget)
        layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

    def setup_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addAction('&File')
        file_menu = menu.addAction('&Edit')
        file_menu = menu.addAction('&Selection')
        file_menu = menu.addAction('&View')
        menu.setStyleSheet('QMenuBar {background-color:#515151; color: #f0f0f0;}')

    def setup_webview(self, file_path):
        self.webview = QWebEngineView()
        self.webview.setMaximumWidth(300)
        self.webview.load(QUrl.fromLocalFile(file_path))
