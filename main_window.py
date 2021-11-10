from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from gui_elements import *
class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.set_defaults()

        self.setup_menubar()
        self.setup_webview(file_path)
        self.setup_left_panel()

        self.setup_layout()

    def set_defaults(self):
        self.setWindowTitle("PZSP2")
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

    def setup_menubar(self):
        self.menu = MyMenuBar()
        self.setup_menubar_actions()
        self.setMenuBar(self.menu)

    def setup_menubar_actions(self):
        file_open_action = QAction(text='Open', parent=self)
        file_open_action.triggered.connect(self.file_open)
        self.menu.file_menu.addAction(file_open_action)

        self.view_change_action = QAction(text='Change view to text editor', parent=self)
        self.view_change_action.triggered.connect(self.change_view)
        self.menu.view_menu.addAction(self.view_change_action)

    def setup_webview(self, file_path):
        self.webview = QWebEngineView()
        self.webview.setFixedWidth(600)
        self.webview.load(QUrl.fromLocalFile(file_path))

    def setup_left_panel(self):
        self.setup_control_panel()
        self.setup_css_editor()
        self.left_panel = QWidget()
        left_panel_layout = QStackedLayout()
        left_panel_layout.addWidget(self.control_panel)
        left_panel_layout.addWidget(self.css_editor)

        self.left_panel.setLayout(left_panel_layout)

    def setup_control_panel(self):
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QComboBox())
        control_panel_layout.addWidget(QComboBox())

        self.control_panel.setLayout(control_panel_layout)

    def setup_css_editor(self):
        self.css_editor = CSSEditor()


    def setup_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def file_open(self):
        print('File opened')

    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')

