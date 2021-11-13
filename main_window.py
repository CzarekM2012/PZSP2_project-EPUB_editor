
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
        self.init_variables()

        self.setup_menubar()
        self.setup_webview()
        self.setup_left_panel()
        self.setup_layout()

 
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
        left_panel_layout.addWidget(self.editor_panel)

        self.left_panel.setLayout(left_panel_layout)


    def setup_control_panel(self):
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()

        self.combo_box_style = QComboBox()
        self.combo_box_style.currentTextChanged.connect(self.change_edit_style)
        
        control_panel_layout.addWidget(self.combo_box_style)
        control_panel_layout.addWidget(QComboBox())
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        control_panel_layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))

        self.control_panel.setLayout(control_panel_layout)


    def setup_css_editor(self):
        self.editor_panel = QWidget()
        editor_panel_layout = QVBoxLayout()

        self.css_editor = CSSEditor()  # Needs to be created before combo_box, because combo_box changes editor's text (and triggers right after creation)
        self.editor_combo_box_file = QComboBox()
        self.editor_combo_box_file.currentTextChanged.connect(self.change_editor_file)
        
        editor_panel_layout.addWidget(self.editor_combo_box_file)
        editor_panel_layout.addWidget(self.css_editor)

        self.editor_panel.setLayout(editor_panel_layout)


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


    def init_variables(self):
        self.current_edit_style = None
        self.edited_css_path = None
        self.file_manager = FileManager()


    # Connected to editor_combo_box_file
    def change_editor_file(self):
        print("TEST")
        self.editor_set_file(self.editor_combo_box_file.currentText())

    # Connected to combo_box_style
    def change_edit_style(self):
        self.set_edit_style(self.combo_box_style.currentText())


    def set_edit_style(self, name):
        
        # Restore original color
        if self.current_edit_style != None:
            self.file_manager.set_css_param(self.current_edit_style, 'color', self.last_color)
        
        self.current_edit_style = name
        
        # Remember original color
        self.last_color = self.file_manager.get_css_param(self.current_edit_style, 'color')
        self.file_manager.set_css_param(self.current_edit_style, 'color', "#ff0000")
        
        self.update_view()


    def update_view(self):
        self.file_manager.update_css()
        self.webview.reload()

    def next_page(self):
        self.show_page(self.current_page_nr+1)


    def prev_page(self):
        self.show_page(self.current_page_nr-1)


    def show_page(self, page_nr):
        self.current_page_nr, self.shown_url = self.file_manager.get_page(page_nr)
        self.webview.load(self.shown_url)


    def editor_set_file(self, relative_path):

        print(relative_path)

        # Save the previous file
        if self.edited_css_path != None:
            self.editor_save_changes()

        # No file specified (eg. action triggererd too early)
        if relative_path == None or relative_path == "":
            self.edited_css_path = None
            self.css_editor.setText("")
            return

        self.css_editor.setText(self.file_manager.get_css_text_by_path(relative_path))
        self.edited_css_path = relative_path
        
    
    def editor_save_changes(self):
        self.file_manager.overwrite_css_file_with_text(self.edited_css_path, self.css_editor.toPlainText())
        #self.file_manager.update_css() # Not needed, overwrite() already writes changes to the file
        self.update_view()

    # Funkcje wykorzystywane prze QAction
    def file_open(self):
        self.file_manager.load_book(QFileDialog.getOpenFileName(self, 'Open Epub', '', 'Epub Files (*.epub)')[0])
        self.editor_set_file(None)
        self.show_page(4)
        self.combo_box_style.addItems(self.file_manager.get_css_style_names())
        self.editor_combo_box_file.addItems(self.file_manager.get_css_file_paths())

    
    def file_save(self):
        self.file_manager.save_book(QFileDialog.getSaveFileName(self, 'Save Epub', '', 'Epub Files (*.epub)')[0])

    
    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')
