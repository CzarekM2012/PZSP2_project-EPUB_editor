from pathlib import Path
from PySide6.QtGui import QAction, QFont, QKeySequence, QIcon
from PySide6.QtWidgets import QFrame, QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSlider, QStackedLayout, QStyleFactory, QToolBar, QVBoxLayout, QWidget, QPushButton, QMessageBox
# from build.nsis.pkgs.PySide6.examples.widgets.widgetsgallery.widgetgallery import style_names
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from gui_elements import *
from file_manager import FileManager
from utility import *

import re
from font import Font

RESULT_SUCCESS = 0 # Return value
RESULT_CANCEL = 2


HIGHLIGHT_COLOR_STRING = "#ffffab"

class MainWindow(QMainWindow):

    def __init__(self, screen_size):
        super(MainWindow, self).__init__()
        self.screen_size = screen_size
        self.set_defaults()
        self.init_variables()
        self.reload_interface()
        self.file_open(Path(__file__).parent / 'books/manual.epub')

    def closeEvent(self, evnt):
        print("Closing")

        result = self.file_save_prompt()
        if result == RESULT_CANCEL:
            evnt.ignore()
            return
        
        super(MainWindow, self).closeEvent(evnt)

    def set_defaults(self):
        self.setWindowTitle("EPUB CSS Editor")
        self.setWindowIcon(QIcon((str(Path(__file__).parent /"resources/icon0.ico"))))
        self.resize(self.screen_size * 0.7)


    def init_variables(self):
        self.current_page_nr = 0
        self.edited_css_path = None
        self.file_manager = FileManager()

        # Load built-in fonts
        self.fonts = {}
        for font_name, fallback_font in font_list_built_in:
            font = Font(font_name, Font.TYPE_NO_FILE, fallback=fallback_font)
            self.fonts[str(font)] = font

        # Import additional fonts from 'fonts' folder
        self.import_fonts()


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

        font_import_action = QAction(text='Import fonts', parent=self)
        font_import_action.setShortcut(QKeySequence('Ctrl+Alt+f'))
        font_import_action.triggered.connect(self.import_fonts)
        self.menu.file_menu.addAction(font_import_action)

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
        self.basic_font_editor = BasicFontEditor(label_style, 'Font', self.change_font, self.set_font_size, self.trigger_basic_css_prop)
        self.combo_box_font = self.basic_font_editor.combo_box  # zmienna wykorzystywana przez stary kod
        self.misc_prop_editor = MiscCSSPropertyEditor(label_style, 'Other properties', self.set_misc_css_prop, self.remove_misc_css_prop, self.update_misc_value)
        self.color_box = ColorBox(label_style, 'Font color', self.change_color_slider, self.color_update_confirm, self.remove_color)

        control_panel_layout.addWidget(self.combo_box_style)
        control_panel_layout.addWidget(self.basic_font_editor)
        control_panel_layout.addWidget(self.color_box)
        control_panel_layout.addWidget(self.misc_prop_editor)

        self.control_panel.setLayout(control_panel_layout)
        

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
        

    def reload_editor_file(self, force=False):
        return self.editor_set_file(self.editor_combo_box_file.currentText(), force)


    # Connected to editor_combo_box_file
    def change_editor_file(self):
        return self.editor_set_file(self.editor_combo_box_file.currentText())


    # Connected to combo_box_font
    def change_font(self):
        style_name = self.get_current_style_name()

        chosen_font = self.combo_box_font.currentText()
        if style_name == "":
            return
            
        if chosen_font == "[None]":
            self.file_manager.remove_css_param(style_name, 'font-family')
            self.update_editor()
            self.check_add_used_fonts()
            return

        font = self.get_font_by_desc(chosen_font)
        if font == None:
            raise Exception(f"Chosen font: |{chosen_font}| has not been found")

        if len(font.fallback.strip()) == 0:
            self.file_manager.set_css_param(style_name, 'font-family', f'{font.name}')
        else:        
            self.file_manager.set_css_param(style_name, 'font-family', f'{font.name}, {font.fallback}')
        
        self.check_add_used_fonts()
        self.update_editor()


    def change_color_slider(self):
        self.change_color_rgb(*self.color_box.get_color_values())

    def color_update_confirm(self):
        self.update_editor()

    def remove_color(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        self.color_box.reset_sliders()
        self.file_manager.remove_css_param(style_name, 'color')
        self.update_editor()


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

    # Connected to combo_box_style
    def change_edit_style(self):
        self.update_editor()


    def set_interface_signal_lock(self, on):
        self.combo_box_font.blockSignals(on)


    def toggle_button_states(self, style_name):
        states_dict = {}
        bold_val = self.file_manager.get_css_param(style_name, 'font-weight')
        italic_val = self.file_manager.get_css_param(style_name, 'font-style')
        decor_vals = self.file_manager.get_css_param(style_name, 'text-decoration')
        decor_vals = decor_vals.split(' ')
        states_dict['bold'] = bold_val == 'bold'
        states_dict['italic'] = italic_val == 'italic'
        states_dict['underline'] = 'underline' in decor_vals
        states_dict['line-through'] = 'line-through' in decor_vals
        self.basic_font_editor.toggle_button_states(states_dict)
    

    def update_font_list(self):
        self.combo_box_font.clear()
        self.combo_box_font.addItem("[None]")
        font_list = self.get_font_descriptions()
        font_list.sort()
        self.combo_box_font.addItems(font_list)

    
    def parse_font_size_str(self, string):
        font_size_str = re.match(r"([0-9.]*)([a-zA-Z%]*)", string)
        font_size = font_size_str.group(1)
        font_size_unit = font_size_str.group(2)
        return font_size, font_size_unit

    
    def get_font_descriptions(self):
        return [str(font) for font_desc, font in self.fonts.items()]

    def get_font_by_name(self, name):
        for font_desc, font in self.fonts.items():
            if name == font.name:
                return font
        return None

    def get_font_by_desc(self, desc):
        for font_desc, font in self.fonts.items():
            if desc in font_desc: # This way to also allow partial match
                return font
        return None

    def get_font_by_css_string(self, name):
        return self.get_font_by_name(Font.get_font_from_css_string(name).name)


    # Checks if all used fonts are in EPUB. Adds or removes fonts otherwise
    def check_add_used_fonts(self):
        used_font_list = self.file_manager.get_used_font_name_list()
        css_font_list = self.file_manager.get_css_font_name_list()

        #print(used_font_list)
        #print(css_font_list)

        for font in used_font_list:
            if font not in css_font_list:
                font_obj = self.get_font_by_name(font)
                if font_obj != None and font_obj.file_type == Font.TYPE_LOCAL_FILE:
                    #print(f"Adding: {str(font_obj)}")
                    self.file_manager.add_font_to_epub(font_obj)
        
        
        # The inner for loop has to be restarted after every remove
        # otherwise, a rare exception may occur that a font is skipped
        # because other font was removed and the list has shortened
        removed = True
        while removed:
            removed = False
            css_font_list = self.file_manager.get_css_font_name_list()
            for font in css_font_list:
                if font not in used_font_list:
                    font_obj = self.get_font_by_name(font)
                    if font_obj != None and font_obj.file_type == Font.TYPE_LOCAL_FILE:
                        #print(f"Removing: {str(font_obj)}")
                        self.file_manager.remove_font_from_epub(font_obj)
                        removed = True
                        break
                

    def get_current_style_name(self):
        return str(self.combo_box_style.currentText())


    def update_editor(self):
        self.update_interface()
        self.update_view()


    # Updates all UI components in the graphical editor
    def update_interface(self):

        self.set_interface_signal_lock(True)

        style_name = self.get_current_style_name()
        
        font_size_str = self.file_manager.get_css_param(style_name, 'font-size')
        current_font_size, current_font_size_unit = self.parse_font_size_str(font_size_str)
        
        self.toggle_button_states(style_name)
        
        if not self.basic_font_editor.is_supported_unit(current_font_size_unit):
            current_font_size_unit = '--'
        self.basic_font_editor.set_font_size_unit(current_font_size_unit)
        self.basic_font_editor.set_font_size(current_font_size)
        
        # Update color sliders
        color = self.file_manager.get_css_param(style_name, 'color')
        if color == "":
            self.color_box.reset_sliders()
        else:
            self.color_box.set_sliders_hex(color)
        
        # Update font selectors, add new fonts to list if missing
        current_font = self.file_manager.get_css_param(style_name, 'font-family')
        #self.check_add_font(current_font)
        
        self.update_font_list()

        font = self.get_font_by_css_string(current_font)
        if font != None:
            index = self.combo_box_font.findText(str(font), Qt.MatchFixedString)
            if index >= 0:
                self.combo_box_font.setCurrentIndex(index)

        self.update_misc_value()

        self.set_interface_signal_lock(False)


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
        if self.page_changed:
            self.page_changed = False
            self.update_editor()
            return
        self.file_manager.update_css()
        self.temporary_changes = False

    def next_page(self):
        self.show_page(self.current_page_nr+1)


    def prev_page(self):
        self.show_page(self.current_page_nr-1)


    def show_page(self, page_nr):
        self.page_changed = True
        self.current_page_nr, self.shown_url = self.file_manager.get_page(page_nr)
        if not self.shown_url == None:
            self.webview.load(self.shown_url)



    # Returns 0 if succeded, otherwise a positive number indicating an error
    def editor_set_file(self, relative_path, force=False):   # force is used to reload file when user switches to editor, because path is the same
        #print(f"Setting editor file path from {self.edited_css_path} to {relative_path} relative_path")

        # Ask to save the previous file, doesn't trigger when toggling from or to empty file to prevent misfires when loading new files
        if self.is_editor_file_changed() and self.edited_css_path != None and relative_path != None and not force:
            choice = self.editor_save_prompt()
            
            if choice == QMessageBox.Save:
                self.editor_save_changes()
            elif choice == QMessageBox.Cancel:
                return RESULT_CANCEL

        # Already handled by checkbox, leaving it here in case it will become useful
        # Switched back to the same file, nothing to do
        #if relative_path == self.edited_css_path and not force:
        #    return 1

        # No file specified (eg. action triggererd too early)
        if relative_path == None or relative_path == "":
            self.edited_css_path = None
            self.css_editor.setText("")
            return 3

        self.css_editor.setText(self.file_manager.get_css_text_by_path(relative_path))
        self.css_editor.highlighter.setDocument(self.css_editor.document())
        self.edited_css_path = relative_path

        return 0
        

    def is_editor_file_changed(self):
        return not self.css_editor.toPlainText() == self.file_manager.get_css_text_by_path(self.edited_css_path)
    

    def editor_save_changes(self):
        self.file_manager.overwrite_css_file_with_text(self.edited_css_path, self.css_editor.toPlainText())
        #self.file_manager.update_css() # Not needed, overwrite() already writes changes to the file
        self.update_editor()


    # Funkcje wykorzystywane prze QAction
    def file_open(self, file: Path = None):

        file_path = file
        if not file_path:
            file_path =  Path(QFileDialog.getOpenFileName(self, 'Open Epub', '', 'Epub Files (*.epub)')[0])
        
        if not file_path.suffix == '.epub':
            return

        result = self.file_manager.load_book(file_path)
        if result > 0:
            self.file_close()
            self.file_open_error()
            return
        
        self.editor_set_file(None) # Need to select a CSS file

        self.import_fonts_from_book()

        self.combo_box_style.clear()
        self.editor_combo_box_file.clear()
        self.combo_box_style.addItems(self.file_manager.get_css_style_names())
        self.editor_combo_box_file.addItems(self.file_manager.get_css_file_paths())

        # TEST
        #font = list(self.fonts.values())[-4]
        #self.file_manager.add_font_to_epub(font)
        #self.file_manager.remove_font_from_epub(font)

        self.show_page(0)


    def import_fonts_from_book(self):
        css_font_list = self.file_manager.get_css_font_name_list()
        css_font_list.extend(self.file_manager.get_used_font_name_list()) # Not sure if needed, but can be useful sometimes

        for font_name in css_font_list:
            if '"' in font_name or '"' in font_name:
                font_name = font_name[1:-1]
            
            font = Font.get_font_from_css_string(font_name)
            font.file_type = Font.TYPE_FROM_EPUB
            
            # A bit crude, but works
            found = False
            for font_2 in list(self.fonts.values()):
                if font_2.name == font.name:
                    found = True
                    break

            if not found: 
                self.fonts[str(font)] = font

        self.update_font_list()

    def file_open_error(self):
        self.display_prompt("Error", "ERROR - could not open file. Not a valid EPUB.", QMessageBox.Ok)


    # Returns a value to check if user wants to proceed or cancel, can also save changes
    def file_save_prompt(self):
        choice = self.display_prompt("Save EPUB", "Are you sure you want to leave this file?\n\nAll unsaved changes will be lost!", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if choice == QMessageBox.Save:
            self.file_save()
        elif choice == QMessageBox.Discard:
            return RESULT_SUCCESS

        return RESULT_CANCEL


    def editor_save_prompt(self):
        return self.display_prompt("Save CSS file", "Some changes have not been saved", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)


    def display_prompt(self, title, message, button_flags):
        prompt = QMessageBox()
        prompt.setWindowTitle(title)
        prompt.setText(message)
        prompt.setStandardButtons(button_flags)
        prompt.setIcon(QMessageBox.Icon(2))
        prompt.setWindowIcon(QIcon(str(Path(__file__).parent /"resources/icon0.ico")))
        return prompt.exec()


    def file_save(self):

        if not self.file_manager.is_file_loaded():
            return
        
        self.file_manager.save_book(QFileDialog.getSaveFileName(self, 'Save Epub', '', 'Epub Files (*.epub)')[0])
        
    def file_close(self):
        self.reload_interface()
        
    
    # Check the "fonts" folder for new fonts
    def import_fonts(self):
        results = list((Path(__file__).parent /"fonts").rglob("*.[tT][tT][fF]"))
        
        for font_path in results:
            font = Font(str(font_path), file_type=Font.TYPE_LOCAL_FILE)
            if str(font) not in self.fonts:
                self.fonts[str(font)] = font
        

    def change_view(self):
        if self.left_panel.layout().currentIndex() == 0:
            self.reload_editor_file(force=True)
            self.left_panel.layout().setCurrentIndex(1)
            self.view_change_action.setText('Change view to basic editor')
        else:
            result = self.reload_editor_file(force=False) # Try to save file
            if result == RESULT_CANCEL:
                self.update_editor()
                return

            self.left_panel.layout().setCurrentIndex(0)
            self.view_change_action.setText('Change view to text editor')
        
        self.update_editor()


    def set_font_size(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        value = self.basic_font_editor.get_font_size()
        unit = self.basic_font_editor.get_font_size_unit()
        if unit == '--':
            font_size_str = self.file_manager.get_css_param(self.get_current_style_name(), 'font-size')
            _, unit = self.parse_font_size_str(font_size_str)

        self.file_manager.set_css_param(style_name, 'font-size', value + unit)
        self.update_editor()


    def trigger_basic_css_prop(self, prop):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        if prop == 'bold':
            self.trigger_bold(style_name)
        elif prop == 'italic':
            self.trigger_italic(style_name)
        elif prop == 'underline':
            self.trigger_underline(style_name)
        else:
            self.trigger_strikeout(style_name)
        
        self.update_editor()
    
    def trigger_bold(self, style_name):
        button_checked = self.basic_font_editor.button_box.bold_button.isChecked()

        if button_checked:
            self.file_manager.set_css_param(style_name, 'font-weight', 'bold')
        else:
            self.file_manager.remove_css_param(style_name, 'font-weight')

    def trigger_italic(self, style_name):
        button_checked = self.basic_font_editor.button_box.italic_button.isChecked()

        if button_checked:
            self.file_manager.set_css_param(style_name, 'font-style', 'italic')
        else:
            self.file_manager.remove_css_param(style_name, 'font-style')

    def trigger_underline(self, style_name):
        current_val = self.file_manager.get_css_param(style_name, 'text-decoration')
        button_val = self.basic_font_editor.button_box.underline_button.isChecked()
        vals = current_val.split(' ')
        if button_val:
            if 'none' in vals:
                vals.remove('none')
            if 'underline' not in vals:
                vals = ['underline'] + vals
        else:
            if 'underline' in vals:
                vals.remove('underline')
        new_val = ' '.join(vals)
        self.file_manager.set_css_param(style_name, 'text-decoration', new_val)

    def trigger_strikeout(self, style_name):
        current_val = self.file_manager.get_css_param(style_name, 'text-decoration')
        button_val = self.basic_font_editor.button_box.strikeout_button.isChecked()
        vals = current_val.split(' ')
        if button_val:
            if 'none' in vals:
                vals.remove('none')
            if 'line-through' not in vals:
                vals = ['line-through'] + vals
        else:
            if 'line-through' in vals:
                vals.remove('line-through')
        new_val = ' '.join(vals)
        self.file_manager.set_css_param(style_name, 'text-decoration', new_val)

    def set_misc_css_prop(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        property = self.misc_prop_editor.get_prop_name()
        value = self.misc_prop_editor.get_value()
        
        self.file_manager.set_css_param(style_name, property, value)

        self.update_editor()


    def remove_misc_css_prop(self):
        self.misc_prop_editor.set_value("")
        
        style_name = self.get_current_style_name()
        if style_name == "":
            return

        property = self.misc_prop_editor.get_prop_name()
        
        self.file_manager.remove_css_param(style_name, property)

        self.update_editor()
    
    def update_misc_value(self):
        style_name = self.get_current_style_name()
        if style_name == "":
            self.misc_prop_editor.set_value("")
            return
        
        value = self.file_manager.get_css_param(style_name, self.misc_prop_editor.property_list.currentText())
        if value == None:
            value = ""
        
        self.misc_prop_editor.set_value(value)    
    

