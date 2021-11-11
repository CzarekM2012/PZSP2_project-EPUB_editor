
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from os import path, listdir, mkdir, unlink, walk
import zipfile
from zipfile import ZIP_DEFLATED, ZipFile
from shutil import rmtree
from gui_elements import *

from reader import Reader
from pathfinder import Pathfinder

import cssutils

class MainWindow(QMainWindow):

    def __init__(self, file_path):
        super(MainWindow, self).__init__()
        self.set_defaults()

        self.setup_menubar()
        self.setup_webview()
        self.setup_left_panel()
        self.setup_layout()

        #self.reader = Reader(file_path)
        self.edition_dir = path.join(path.dirname(__file__), 'edit')
        self.pathfinder = Pathfinder(self.edition_dir)

        #self.webview.load(QUrl.fromLocalFile(file_path))

        #self.show_page(page_nr=self.page_nr_current)

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

    def prepare_edition_dir(self) -> None:
        if path.isdir(self.edition_dir):
            for filename in listdir(self.edition_dir):
                file_path = path.join(self.edition_dir, filename)
                try:
                    if path.isfile(file_path) or path.islink(file_path):
                        unlink(file_path)
                    elif path.isdir(file_path):
                        rmtree(file_path)
                except OSError as e:
                    # Probably only open file or lack of permissions
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            mkdir(self.edition_dir)

    def load_book(self, file_path) -> None:
        self.prepare_edition_dir()
        book = ZipFile(file_path)
        book.extractall(self.edition_dir)
        book.close()
        self.pathfinder.search()
        self.page_nr_current = 0
        self.page_count = len(self.pathfinder.spine)
        print("TEST")
        css_file_paths = self.pathfinder.get_css_path_list()
        css_files = []
        for i in range(len(css_file_paths)):
            css_files.append(cssutils.parseFile(css_file_paths[i]))
        print(css_files)

        for item in css_files[1].cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
            item.style.setProperty("color", "#00ff00")
            #for property in item.style.getProperties():
                #if property.name == "color":
                #    property.value = "#00ff00"

        for item in css_files[1].cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
            for property in item.style.getProperties():
                print(property)

        print(css_files[1].cssText)

        css_file = open(css_file_paths[1], "wb")
        css_file.write(css_files[1].cssText)



    def load_css(self) -> None:
        css_file_path = path.join(self.edition_dir,
                                  self.pathfinder.stylesheets[0])
        with open(css_file_path) as file:
            stylesheet = ''.join(file.readlines())
        self.css_editor.setText(stylesheet)

    def save_book(self, save_path) -> None:
        # folder_name = path.splitext(path.basename(save_path))[0]
        # will get permission error if there is a folder with name "folder_name"
        # in save_dir
        book = ZipFile(save_path, 'w', ZIP_DEFLATED)
        for root, dirs, files in walk(self.edition_dir):
            for file in files:
                book.write(path.join(root, file),
                           path.relpath(path.join(root, file),
                                        self.edition_dir))
        book.close()

    def next_page(self):
        self.show_page(self.page_nr_current+1)

    def prev_page(self):
        self.show_page(self.page_nr_current-1)

    def show_page(self, page_nr):

        # Determine correct page number
        if page_nr < 0:
            self.page_nr_current = self.page_count-1
        elif page_nr >= self.page_count:
            self.page_nr_current = 0
        else:
            self.page_nr_current = page_nr

        page_file_path = path.join(self.edition_dir,
                                   self.pathfinder.spine[self.page_nr_current])
        url = QUrl.fromLocalFile(page_file_path)
        self.webview.load(url)

        # Getting actual content without unpacking the file
        # self.shown_document = self.book.get_item_with_id(self.book.spine[self.page_nr_current][0])

        # Stylesheet needs to be manually added the HTML document, because it's not a file that a browser can find
        # content = self.shown_document.content
        # content += self.stylesheet
        # pos = content.find(b'<link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css" />  <link href="../Styles/page_styles.css" rel="stylesheet" type="text/css" />')
        # l = len(b'<link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css" />  <link href="../Styles/page_styles.css" rel="stylesheet" type="text/css" />')
        # content = content[:pos] + content[pos+l:]

        # print(content.decode("utf-8"))
        #page = self.reader.get_page_content(page_nr)
        #stylesheet = self.reader.get_stylesheet()
        #content = page + b'<style>\n' + stylesheet + b'\n</style>'
        #self.reader.get_fonts()

        #self.webview.setContent(content, 'text/html;charset=UTF-8')

    def get_page_count(self):
        return len(self.book.spine)

    # Funkcje wykorzystywane prze QAction
    def file_open(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open Epub', '', 'Epub Files (*.epub)')[0]
        self.original_file_path = path.abspath(file_path)
        self.load_book(self.original_file_path)
        self.load_css()
        self.show_page(4)
        print('File opened')

    def file_save(self):
        new_file_path = self.original_file_path[:-5] + '-edited' + self.original_file_path[-5:]
        file_path = QFileDialog.getSaveFileName(self, 'Save Epub', new_file_path, 'Epub Files (*.epub)')[0]
        self.save_book(path.abspath(file_path))
        print('File saved')

    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')
