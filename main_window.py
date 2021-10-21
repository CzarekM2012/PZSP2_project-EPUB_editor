from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QSlider, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PZSP2")
        self.setStyleSheet('MainWindow {background-color:#7d7d7d}')
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

        self.setup_menubar()
        self.setup_webview(file_path)
        self.setup_control_panel()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def setup_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addAction('&File')
        edit_menu = menu.addAction('&Edit')
        selection_menu = menu.addAction('&Selection')
        view_menu = menu.addAction('&View')
        menu.setStyleSheet('QMenuBar {background-color:#515151; color: #f0f0f0;}')

    def setup_webview(self, file_path):
        self.webview = QWebEngineView()
        self.webview.setFixedWidth(600)
        self.webview.load(QUrl.fromLocalFile(file_path))

    def setup_control_panel(self):
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QComboBox())
        control_panel_layout.addWidget(QComboBox())

        self.control_panel.setLayout(control_panel_layout)


