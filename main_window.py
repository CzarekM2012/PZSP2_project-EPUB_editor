
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from gui_elements import *
from file_manager import FileManager

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.set_defaults()

        self.setup_menubar()
        self.setup_webview()
        self.setup_left_panel()
        self.setup_layout()

        self.file_manager = FileManager()

 
    def setup_menubar(self):
        self.menu = MyMenuBar()
        self.setup_menubar_actions()
        self.setMenuBar(self.menu)

 
    def setup_menubar_actions(self):
        file_open_action = QAction(text='Open', parent=self)
        file_open_action.triggered.connect(self.file_open)
        file_open_action.setShortcut(QKeySequence('Ctrl+o'))
        self.menu.file_menu.addAction(file_open_action)

        file_save_action = QAction(text='Save', parent=self)
        file_save_action.setShortcut(QKeySequence('Ctrl+s'))
        file_save_action.triggered.connect(self.file_save)
        self.menu.file_menu.addAction(file_save_action)

        self.view_change_action = QAction(text='Change view to text editor', parent=self)
        self.view_change_action.setShortcut(QKeySequence('Ctrl+Alt+v'))
        self.view_change_action.triggered.connect(self.change_view)
        self.menu.view_menu.addAction(self.view_change_action)

        next_page_action = QAction(text='Next page', parent=self)
        next_page_action.setShortcut(QKeySequence('Ctrl+.'))
        next_page_action.triggered.connect(self.next_page)
        self.menu.view_menu.addAction(next_page_action)

        prev_page_action = QAction(text='Previous page', parent=self)
        prev_page_action.setShortcut(QKeySequence('Ctrl+,'))
        prev_page_action.triggered.connect(self.prev_page)
        self.menu.view_menu.addAction(prev_page_action)

 
    def setup_webview(self):
        self.webview = MyWebView()
        self.webview.setFixedWidth(600)

 
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


    def set_defaults(self):
        self.setWindowTitle("PZSP2")
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

 
    def next_page(self):
        self.show_page(self.current_page_nr+1)


    def prev_page(self):
        self.show_page(self.current_page_nr-1)


    def show_page(self, page_nr):

        self.current_page_nr, self.shown_url = self.file_manager.get_page(page_nr)
        self.webview.load(self.shown_url)


    # Funkcje wykorzystywane prze QAction
    def file_open(self):
        self.file_manager.load_book(QFileDialog.getOpenFileName(self, 'Open Epub', '', 'Epub Files (*.epub)')[0])
        self.css_editor.setText(self.file_manager.get_stylesheet_text(0))
        self.show_page(4)
        print('File opened')

    
    def file_save(self):
        self.file_manager.save_book(QFileDialog.getSaveFileName(self, 'Save Epub', '', 'Epub Files (*.epub)')[0])

    
    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')
