from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QToolBar, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PZSP2")

        menu = self.menuBar()
        file_menu = menu.addAction('&File')

        self.webview = self.setup_webview(file_path)
        temp_widget = QLabel("temp")
        temp_widget.setMinimumWidth(300)

        layout = QHBoxLayout()
        layout.addWidget(temp_widget)
        layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

    def setup_webview(self, file_path):
        webview = QWebEngineView()
        webview.setMaximumWidth(300)
        webview.load(QUrl.fromLocalFile(file_path))
        return webview
