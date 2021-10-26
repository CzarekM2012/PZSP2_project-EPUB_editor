from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QSlider, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from ebooklib import epub
import ebooklib

class MainWindow(QMainWindow):

    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PZSP2")
        self.setStyleSheet('MainWindow {background-color:#7d7d7d}')
        self.setFixedHeight(720)
        self.setFixedWidth(1280)

        self.setup_menubar()
        self.setup_control_panel()
        self.setup_webview()
        
        self.load_file(file_path)
        
        self.show_page(4)
       
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.webview)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)


    def load_file(self, file_path):
        self.book = epub.read_epub(file_path)
        self.prepare_css()


    def next_page(self):
        self.show_page(self.page_nr_current+1)
    
    def prev_page(self):
        self.show(self.page_nr_current-1)

    def show_page(self, page_nr):

        # Determine correct page number
        if page_nr < 0:
            self.page_nr_current = self.get_page_count()
        
        elif page_nr > self.get_page_count():
            self.page_nr_current = 0
        
        else:
            self.page_nr_current = page_nr

        # Getting actual content without unpacking the file
        self.shown_document = self.book.get_item_with_id(self.book.spine[self.page_nr_current][0])
        
        # Stylesheet needs to be manually added the HTML document, because it's not a file that a browser can find
        content = self.shown_document.content
        content += self.stylesheet
        #pos = content.find(b'<link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css" />  <link href="../Styles/page_styles.css" rel="stylesheet" type="text/css" />')
        #l = len(b'<link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css" />  <link href="../Styles/page_styles.css" rel="stylesheet" type="text/css" />')
        #content = content[:pos] + content[pos+l:]
        
        print(content.decode("utf-8"))
        self.webview.setContent(content, 'text/html;charset=UTF-8')

    def get_page_count(self):
        return len(self.book.spine)


    # Compiles a big stylesheet containing all CSS files
    # has to be called on document load/change
    def prepare_css(self):
        items = self.book.get_items_of_type(ebooklib.ITEM_STYLE)
        
        stylesheet = b'<style>\n'
        for item in items:
            stylesheet += item.content
        stylesheet += b'\n</style>'

        self.stylesheet = stylesheet


    def setup_menubar(self):
        menu = self.menuBar()
        file_menu = menu.addAction('&File')
        edit_menu = menu.addAction('&Edit')
        selection_menu = menu.addAction('&Selection')
        view_menu = menu.addAction('&View')
        menu.setStyleSheet('QMenuBar {background-color:#515151; color: #f0f0f0;}')

    def setup_webview(self):
        self.webview = QWebEngineView()
        self.webview.setFixedWidth(600)

    def setup_control_panel(self):
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QComboBox())
        control_panel_layout.addWidget(QComboBox())

        self.control_panel.setLayout(control_panel_layout)


