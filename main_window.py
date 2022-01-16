from os import path
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import QFrame, QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget, QPushButton, QMessageBox
# from build.nsis.pkgs.PySide6.examples.widgets.widgetsgallery.widgetgallery import style_names
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from gui_elements import *
from file_manager import FileManager
from utility import *

import re
import time
import threading

HIGHLIGHT_COLOR_STRING = "#ffffab"


class MainWindow(QMainWindow):

    def __init__(self, screen_size):
        super(MainWindow, self).__init__()
        self.screen_size = screen_size
        self.set_defaults()
        self.init_variables()
        self.reload_interface()
        self.file_open(path.join(path.dirname(__file__), 'books/manual.epub'))


    def set_defaults(self):
        self.setWindowTitle("EPUB CSS Editor")
        # self.setFixedHeight(720)
        # self.setFixedWidth(1280)
        self.resize(self.screen_size * 0.7)


    def init_variables(self):
        self.current_page_nr = 0
        self.edited_css_path = None
        self.file_manager = FileManager()


    def reload_interface(self):
        self.setup_menubar()
        self.setup_right_panel()
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


    def setup_right_panel(self):
        self.setup_webview()
        self.setup_page_control_buttons()
        self.right_panel = QWidget()
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setContentsMargins(10,0,10,10)
        right_panel_layout.addWidget(self.page_control_buttons)
        right_panel_layout.addWidget(self.webview)
        self.right_panel.setLayout(right_panel_layout)
 

    def setup_webview(self):
        self.webview = MyWebView()
        self.webview.loadFinished.connect(self.on_webview_reload)

    
    def setup_page_control_buttons(self):
        self.page_control_buttons = QWidget()
        self.page_control_buttons.setMaximumHeight(50)
        page_control_buttons_layout = QHBoxLayout()
        page_control_buttons_layout.setContentsMargins(0,0,0,0)

        font = QFont()
        font.setPointSize(20)
        self.prev_page_button = QPushButton(text='◀', font=font)
        self.prev_page_button.clicked.connect(self.prev_page)
        page_control_buttons_layout.addWidget(self.prev_page_button)
        self.next_page_button = QPushButton(text='▶', font=font)
        self.next_page_button.clicked.connect(self.next_page)
        page_control_buttons_layout.addWidget(self.next_page_button)

        self.page_control_buttons.setLayout(page_control_buttons_layout)

 
    def setup_left_panel(self):
        self.setup_control_panel()
        self.setup_css_editor()
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(400)
        left_panel_layout = QStackedLayout()
        left_panel_layout.addWidget(self.control_panel)
        left_panel_layout.addWidget(self.editor_panel)

        self.left_panel.setLayout(left_panel_layout)


    def setup_control_panel(self):
        label_style = "QLabel { color : #448aff; font-size: 9pt; }"
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()

        self.combo_box_style = ControlPanelComboBox(label_style, 'CSS style', self.change_edit_style)

        self.basic_font_editor = BasicFontEditor(label_style, 'Font', self.change_font, self.set_font_size)
        self.combo_box_font = self.basic_font_editor.combo_box  # zmienna wykorzystywana przez stary kod
        self.misc_css_property_editor = MiscCSSPropertyEditor(label_style, 'Other properties')
        self.color_box = ColorBox(label_style, 'Font color', self.change_color_slider, self.remove_color)

        control_panel_layout.addWidget(self.combo_box_style)
        control_panel_layout.addWidget(self.basic_font_editor)
        control_panel_layout.addWidget(self.color_box)
        control_panel_layout.addWidget(self.misc_css_property_editor)

        self.control_panel.setLayout(control_panel_layout)

    def get_font_names(self):
        return [item[0] for item in font_list]
        

    def setup_css_editor(self):
        self.editor_panel = QWidget()
        editor_panel_layout = QVBoxLayout()

        self.css_editor = CSSEditor()  # Needs to be created before combo_box, because combo_box changes editor's text (and triggers right after creation)
        
        self.editor_combo_box_file = QComboBox()
        self.editor_combo_box_file.currentTextChanged.connect(self.change_editor_file)

        self.editor_button_save = QPushButton("Save")
        self.editor_button_save.clicked.connect(self.editor_save_changes)

        editor_panel_layout.addWidget(self.editor_combo_box_file)
        editor_panel_layout.addWidget(self.editor_button_save)
        editor_panel_layout.addWidget(self.css_editor)

        self.editor_panel.setLayout(editor_panel_layout)


    def setup_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)


    def reload_editor_file(self):
        self.editor_set_file(self.editor_combo_box_file.currentText())

    # Connected to editor_combo_box_file
    def change_editor_file(self):
        self.editor_set_file(self.editor_combo_box_file.currentText())


    # Connected to combo_box_font
    def change_font(self):
        style_name = self.get_current_style_name()

        chosen_font = self.combo_box_font.currentText()
        if style_name == "":
            return
            
        if chosen_font == "[None]":
            self.file_manager.remove_css_param(style_name, 'font-family')
            self.update_view()
            return

        for font, backup_font in font_list:
            if font == chosen_font:
                self.file_manager.set_css_param(style_name, 'font-family', f'"{font}", {backup_font}')
                #print(self.file_manager.get_css_param(style_name, 'font-family'))
                break
        
        self.update_view()

    def change_color_slider(self):
        self.change_color_rgb(*self.color_box.get_color_values())

    def remove_color(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        self.color_box.reset_sliders()
        self.file_manager.remove_css_param(style_name, 'color')
        self.update_view()

    def change_color_rgb(self, r, g, b):
        """
        Sets the color of selected style to given rgb values.
        Value range: 0-255
        """
        style_name = self.get_current_style_name()
        if style_name == "":
            return
        
        #print(f"Setting color to: RGB({r}, {g}, {b})")
        hex_string = rgb_to_hex(r, g, b)
        self.color_box.set_color_label(f"Color: RGB ({r}, {g}, {b}) = {hex_string}")
        #print(f"Setting color to: {hex_string}")

        self.file_manager.set_css_param(style_name, 'color', hex_string)
        self.update_view()

    # Connected to combo_box_style
    def change_edit_style(self):
        
        # Update color sliders
        color = self.file_manager.get_css_param(self.get_current_style_name(), 'color')
        if color == "":
            self.color_box.reset_sliders()
        else:
            self.color_box.set_sliders_hex(color)
        
        # Update font selectors, add new fonts to list if missing
        current_font = self.file_manager.get_css_param(self.get_current_style_name(), 'font-family')
        self.check_add_font(current_font)
        
        self.combo_box_font.clear()
        self.combo_box_font.addItem("[None]")
        self.combo_box_font.addItems(self.get_font_names())

        
        font_size_str = self.file_manager.get_css_param(self.get_current_style_name(), 'font-size')
        font_size_str = re.match(r"([0-9.]*)([a-zA-Z%]*)", font_size_str)
        current_font_size = font_size_str.group(1)
        self.basic_font_editor.set_font_size(current_font_size)
        current_font_size_unit = font_size_str.group(2)
        self.basic_font_editor.set_font_size_unit(current_font_size_unit)

        for font_name, fallback_font in font_list:
            if font_name in current_font:
                index = self.combo_box_font.findText(font_name, Qt.MatchFixedString)
                if index >= 0:
                    self.combo_box_font.setCurrentIndex(index)

        self.update_view()
    

    def check_add_font(self, font_desc):
        """
        Adds a font from a CSS descriptor like '"Font", another-font' to the font_list
        First checks if such font already exists in the list
        """
        # TODO: Check CSS guidline compliance
        if font_desc == "" or font_desc == None:
            return

        font_name = ""
        fallback_font = "serif"
        sign = ""
        if '"' in font_desc:
            sign = '"'
        elif "'" in font_desc:
            sign = "'"
        else:
            font_name = font_desc

        if sign != "":
            start = font_desc.find(sign) + len(sign)
            end = font_desc.find(sign, start + len(sign))
            font_name = font_desc[start:end]
            
            if "sans-serif" in font_desc[:start] or "sans-serif" in font_desc[end:]:
                fallback_font = "sans-serif"
            
            elif "monospace" in font_desc[:start] or "monospace" in font_desc[end:]:
                fallback_font = "monospace"

            elif "cursive" in font_desc[:start] or "cursive" in font_desc[end:]:
                fallback_font = "cursive"

        font_tuple = (font_name, fallback_font)
        if font_tuple not in font_list:
            font_list.append(font_tuple)

        

    def get_current_style_name(self):
        return str(self.combo_box_style.currentText())


    def update_view(self):
        """
        Updates the text display on the right side.
        Also applies temporary changes like currently-edited style highlight 
        """
        style_name = self.get_current_style_name()

        # Highlight chosen style when control_panel is shown
        if self.left_panel.layout().currentIndex() == 0 and style_name != "":

            self.last_color = self.file_manager.get_css_param(style_name, 'background-color')
            self.file_manager.set_css_param(style_name, 'background-color', HIGHLIGHT_COLOR_STRING)
            self.temporary_changes = True

            self.file_manager.update_css()
            self.webview.reload()

            self.file_manager.set_css_param(style_name, 'background-color', self.last_color)
            return

        # No temporary changes, just save and draw
        self.file_manager.update_css()
        self.webview.reload()

    def on_webview_reload(self):
        self.file_manager.update_css()
        self.temporary_changes = False

    def next_page(self):
        self.show_page(self.current_page_nr+1)


    def prev_page(self):
        self.show_page(self.current_page_nr-1)


    def show_page(self, page_nr):
        self.current_page_nr, self.shown_url = self.file_manager.get_page(page_nr)
        if not self.shown_url == None:
            self.webview.load(self.shown_url)


    def editor_set_file(self, relative_path):

        print(relative_path)

        # Save the previous file
        #if self.edited_css_path != None:
        #    self.editor_save_changes()

        # No file specified (eg. action triggererd too early)
        if relative_path == None or relative_path == "":
            self.edited_css_path = None
            self.css_editor.setText("")
            return

        self.css_editor.setText(self.file_manager.get_css_text_by_path(relative_path))
        self.css_editor.highlighter.setDocument(self.css_editor.document())
        self.edited_css_path = relative_path
        
    
    def editor_save_changes(self):
        self.file_manager.overwrite_css_file_with_text(self.edited_css_path, self.css_editor.toPlainText())
        #self.file_manager.update_css() # Not needed, overwrite() already writes changes to the file
        self.update_view()

    # Funkcje wykorzystywane prze QAction
    def file_open(self, file=''):
        if file:
            opened = self.file_manager.load_book(file)
        else:
            opened = self.file_manager.load_book(QFileDialog.getOpenFileName(self, 'Open Epub', '', 'Epub Files (*.epub)')[0])
        if opened == 1:
            self.file_close()
            return
        elif opened == 2:
            self.file_close()
            self.file_open_error()
            return
        
        self.editor_set_file(None) # Need to select a CSS file
        self.show_page(4)

        self.combo_box_style.clear()
        self.editor_combo_box_file.clear()
        self.combo_box_style.addItems(self.file_manager.get_css_style_names())
        self.editor_combo_box_file.addItems(self.file_manager.get_css_file_paths())

    def file_save(self):

        if not self.file_manager.is_file_loaded():
            return
        
        self.file_manager.save_book(QFileDialog.getSaveFileName(self, 'Save Epub', '', 'Epub Files (*.epub)')[0])
        
    def file_close(self):
        self.reload_interface()
        
    
    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.reload_editor_file()
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')
        
        self.update_view()

    def set_font_size(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        value = self.basic_font_editor.get_font_size()
        unit = self.basic_font_editor.get_font_size_unit()

        self.file_manager.set_css_param(style_name, 'font-size', value + unit)
        self.update_view()


