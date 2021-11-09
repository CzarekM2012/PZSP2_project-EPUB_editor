from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QSlider, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from gui_elements import *
class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.set_defaults()

        self.setup_menubar()
        self.setup_webview(file_path)
        self.setup_control_panel()

        self.setup_layout()

    def set_defaults(self):
        self.setWindowTitle("PZSP2")
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

    def setup_menubar(self):
        menu = MyMenuBar()
        file_open_action = QAction(text='Open', parent=self)
        file_open_action.triggered.connect(self.file_open)
        menu.file_menu.addAction(file_open_action)
        self.setMenuBar(menu)

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

    def setup_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def file_open(self):
        print('File opened')


