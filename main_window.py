from os import path
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget, QPushButton, QMessageBox
# from build.nsis.pkgs.PySide6.examples.widgets.widgetsgallery.widgetgallery import style_names
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from gui_elements import *
from file_manager import FileManager

import time
import threading

HIGHLIGHT_COLOR_STRING = "#ffffab"

font_list = [
    ("Arial", "sans-serif"),
    ("Verdana", "sans-serif"),
    ("Helvetica", "sans-serif"),
    ("Tahoma", "sans-serif"),
    ("Trebuchet MS", "sans-serif"),
    ("Times New Roman", "serif"),
    ("Georgia", "serif"),
    ("Garamond", "serif"),
    ("Courier New", "monospace"),
    ("Brush Script MT", "cursive"),
]

def rgb_to_hex(r, g, b):
    """
    Takes values from range 0-255 and returns a hex string in format "RRGGBB"
    """
    return '#%02x%02x%02x' % (r, g, b)

def hex_to_rgb(hex_string):
    """
    String has to be formatted this way: "RRGGBB" or "RGB" (shorthand version)
    Returns a tuple of integers like (R, G, B), where each value is in range 0-255
    """
    #print(f'String to parse: "{hex_string}"')

    if len(hex_string) == 6:                # Classic hex string
        r = int("0x" + hex_string[:2], 0)
        g = int("0x" + hex_string[2:4], 0)
        b = int("0x" + hex_string[4:], 0)
    elif len(hex_string) == 3:              # Shorthand hex string
        r = int("0x" + hex_string[0] + hex_string[0], 0)
        g = int("0x" + hex_string[1] + hex_string[1], 0)
        b = int("0x" + hex_string[2] + hex_string[2], 0)
    else :                                  # Not a valid hex string
        return None
    return (r, g, b)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.set_defaults()
        self.init_variables()
        self.reload_interface()
        self.file_open(path.join(path.dirname(__file__), 'books/manual.epub'))


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
        left_panel_layout = QStackedLayout()
        left_panel_layout.addWidget(self.control_panel)
        left_panel_layout.addWidget(self.editor_panel)

        self.left_panel.setLayout(left_panel_layout)


    def setup_control_panel(self):
        self.control_panel = QWidget()
        control_panel_layout = QVBoxLayout()

        self.combo_box_style = QComboBox()
        self.combo_box_style.currentTextChanged.connect(self.change_edit_style)

        self.combo_box_font = QComboBox()
        self.combo_box_font.currentTextChanged.connect(self.change_font)
        
        self.color_box = QWidget()
        color_box_layout = QVBoxLayout()
        self.color_label = QLabel(text="No color specified")
        self.color_label.setFont(QFont('Arial', 20))
        self.slider_color_r = QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider_color_g = QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider_color_b = QSlider(orientation=Qt.Orientation.Horizontal)
        self.slider_color_r.setMinimum(0)
        self.slider_color_r.setMaximum(255)
        self.slider_color_r.setSingleStep(1)
        self.slider_color_g.setMinimum(0)
        self.slider_color_g.setMaximum(255)
        self.slider_color_g.setSingleStep(1)
        self.slider_color_b.setMinimum(0)
        self.slider_color_b.setMaximum(255)
        self.slider_color_b.setSingleStep(1)
        self.slider_color_r.valueChanged.connect(self.change_color_slider)
        self.slider_color_g.valueChanged.connect(self.change_color_slider)
        self.slider_color_b.valueChanged.connect(self.change_color_slider)
        self.color_remove_button = QPushButton(text="Remove color")
        self.color_remove_button.clicked.connect(self.remove_color)
        color_box_layout.addWidget(self.color_label)
        color_box_layout.addWidget(self.slider_color_r)
        color_box_layout.addWidget(self.slider_color_g)
        color_box_layout.addWidget(self.slider_color_b)
        color_box_layout.addWidget(self.color_remove_button)
        self.color_box.setLayout(color_box_layout)
        self.color_box.setFixedHeight(170)

        control_panel_layout.addWidget(self.combo_box_style)
        control_panel_layout.addWidget(self.combo_box_font)
        control_panel_layout.addWidget(self.color_box)

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


    def set_defaults(self):
        self.setWindowTitle("Edytor EPUB")
        self.setFixedHeight(720)
        self.setFixedWidth(1280)


    def init_variables(self):
        self.current_page_nr = 0
        self.edited_css_path = None
        self.file_manager = FileManager()

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
        self.change_color_rgb(self.slider_color_r.value(),
                              self.slider_color_g.value(),
                              self.slider_color_b.value())

    def remove_color(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        self.reset_color_sliders()
        self.file_manager.remove_css_param(style_name, 'color')
        self.update_view()

    def set_color_sliders_enabled(self, enable):
        """
        Enables or disables (and resets) color sliders when given True or False respectively
        """
        self.slider_color_r.setEnabled(enable)
        self.slider_color_g.setEnabled(enable)
        self.slider_color_b.setEnabled(enable)
        
        self.reset_color_sliders()

    def block_color_slider_signals(self, block):
        """
        Prevents sliders from triggering their functions when values change
        """
        self.slider_color_r.blockSignals(block)
        self.slider_color_g.blockSignals(block)
        self.slider_color_b.blockSignals(block)

    def reset_color_sliders(self):
        self.set_color_sliders(0, 0, 0)
        self.color_label.setText(f"No color specified")

    def set_color_sliders(self, r, g, b):
        """
        Sets slider values without triggering updates to avoid unnecessary file writes and update loops
        Also keeps color label up to date
        """
        self.block_color_slider_signals(True)
        self.slider_color_r.setValue(r)
        self.slider_color_g.setValue(g)
        self.slider_color_b.setValue(b)
        self.block_color_slider_signals(False)
        
        hex_string = rgb_to_hex(r, g, b)
        self.color_label.setText(f"Color: RGB ({r}, {g}, {b}) = {hex_string}")


    def set_color_sliders_hex(self, hex_string):
        r, g, b = hex_to_rgb(hex_string[1:])
        self.set_color_sliders(r, g, b)

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
        self.color_label.setText(f"Color: RGB ({r}, {g}, {b}) = {hex_string}")
        #print(f"Setting color to: {hex_string}")

        
        self.file_manager.set_css_param(style_name, 'color', hex_string)
        self.update_view()
        pass

    # Connected to combo_box_style
    def change_edit_style(self):
        
        # Update color sliders
        color = self.file_manager.get_css_param(self.get_current_style_name(), 'color')
        if color == "":
            self.reset_color_sliders()
        else:
            self.set_color_sliders_hex(color)
        
        # Update font selectors, add new fonts to list if missing
        current_font = self.file_manager.get_css_param(self.get_current_style_name(), 'font-family')
        self.check_add_font(current_font)
        
        self.combo_box_font.clear()
        self.combo_box_font.addItem("[None]")
        self.combo_box_font.addItems(self.get_font_names())

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


    def file_open_error(self):
        error = QMessageBox()
        error.setText("ERROR - could not open file. Not a valid EPUB.")
        error.setWindowTitle("Error")
        error.exec()


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


