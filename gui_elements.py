from cProfile import label
from msilib.schema import ControlEvent
from tkinter import Toplevel
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QMenuBar, QSlider, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QFrame
from highlighter import Highlighter
from utility import hex_to_rgb, rgb_to_hex


class MyMenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        self.file_menu = self.addMenu('&File')
        self.edit_menu = self.addMenu('&Edit')
        self.selection_menu = self.addMenu('&Selection')
        self.view_menu = self.addMenu('&View')


class MyWebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setPage(MyWebEnginePage(self))
        self.setMinimumWidth(400)
        self.setContextMenuPolicy(Qt.NoContextMenu)


class MyWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, type, isMainFrame) -> bool:
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

    def __repr__(self):
        return 'MyPage'


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QSlider(orientation=Qt.Orientation.Horizontal))
        layout.addWidget(QComboBox())
        layout.addWidget(QComboBox())

        self.setLayout(layout)


class CSSEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setTextColor("white")
        self.highlighter = Highlighter()
        self.highlighter.setup()


class ControlPanelElement(QWidget):
    def __init__(self, label_style, label_text):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)

        self.label = QLabel(label_text)
        self.label.setStyleSheet(label_style)

        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)


class ControlPanelComboBox(ControlPanelElement):
    def __init__(self, label_style, label_text, action):
        super().__init__(label_style, label_text)
        self.setFixedHeight(60)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(action)

        self.main_layout.addWidget(self.combo_box)

    def currentText(self):
        return self.combo_box.currentText()

    def clear(self):
        self.combo_box.clear()

    def addItems(self, items):
        self.combo_box.addItems(items)

    def addItem(self, item):
        self.combo_box.addItem(item)

    def findText(self, string, match_flag):
        self.combo_box.findText(string, match_flag)

    def setCurrentIndex(self, index):
        self.combo_box.setCurrentIndex(index)


class BasicFontEditor(ControlPanelElement):
    def __init__(self, label_style, label_text, combo_box_action, font_size_picker_action):
        super().__init__(label_style, label_text)
        self.setFixedHeight(160)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(combo_box_action)
        self.font_size_picker = FontSizePicker(font_size_picker_action)
        self.button_box = ButtonBox()

        self.main_layout.addWidget(self.combo_box)
        self.main_layout.addWidget(self.font_size_picker)
        self.main_layout.addWidget(self.button_box)

    def get_font_size(self):
        return self.font_size_picker.get_font_size()

    def get_font_size_unit(self):
        return self.font_size_picker.get_font_size_unit()

    def set_font_size(self, value):
        self.font_size_picker.set_font_size(value)

    def set_font_size_unit(self, value):
        self.font_size_picker.set_font_size_unit(value)

class ButtonBox(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        font = QFont('', pointSize=16)
        self.bold_button = QPushButton(text='B', font=font)
        self.bold_button.setCheckable(True)

        font = QFont('', pointSize=16, italic=True)
        self.italic_button = QPushButton(text='I', font=font)
        self.italic_button.setCheckable(True)

        font = QFont('', pointSize=16)
        font.setUnderline(True)
        self.underline_button = QPushButton(text='U', font=font)
        self.underline_button.setCheckable(True)

        font = QFont('', pointSize=16)
        font.setStrikeOut(True)
        self.strikeout_button = QPushButton(text='ab', font=font)
        self.strikeout_button.setCheckable(True)

        layout.addWidget(self.bold_button)
        layout.addWidget(self.italic_button)
        layout.addWidget(self.underline_button)
        layout.addWidget(self.strikeout_button)
        self.setLayout(layout)


class FontSizePicker(QWidget):

    UNITS = ['mm', 'px', 'pt', 'em', 'ex', 'vw', 'vh', '%']

    def __init__(self, action):
        super().__init__()
        self.action = action
        self.setFixedHeight(50)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.decrease_button = QPushButton('-')
        self.decrease_button.released.connect(self._decrease_font_size)
        self.increase_button = QPushButton('+')
        self.increase_button.released.connect(self._increase_font_size)
        self.size_field = QLineEdit()
        self.size_field.setValidator(QDoubleValidator(0, 500, 3))
        self.size_field.editingFinished.connect(action)
        self.unit_picker = QComboBox()
        self.unit_picker.addItems(self.UNITS)
        self.unit_picker.currentIndexChanged.connect(action)

        layout.addWidget(self.decrease_button)
        layout.addWidget(self.increase_button)
        layout.addWidget(self.size_field)
        layout.addWidget(self.unit_picker)
        self.setLayout(layout)

    def _increase_font_size(self):
        value = float(self.get_font_size())
        value += 1
        self.size_field.setText(str(value))
        self.action()

    def _decrease_font_size(self):
        value = float(self.get_font_size())
        value = max(value - 1, 0)
        self.size_field.setText(str(value))
        self.action()

    def get_font_size(self):
        return self.size_field.text()

    def get_font_size_unit(self):
        return self.unit_picker.currentText()

    def set_font_size(self, value):
        self.size_field.setText(value)

    def set_font_size_unit(self, value):
        self.unit_picker.setCurrentText(value)


class MiscCSSPropertyEditor(ControlPanelElement):
    def __init__(self, label_style, label_text):
        super().__init__(label_style, label_text)
        self.setFixedHeight(120)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0,0,0,0)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0,0,0,0)
        main_widget = QWidget()

        top_panel = QWidget()
        top_panel.setFixedHeight(50)
        bottom_panel = QWidget()
        bottom_panel.setFixedHeight(50)
        self.property_list = QComboBox()
        self.value_field = QLineEdit()
        self.save_button = QPushButton('save')
        self.delete_button = QPushButton('delete')

        top_layout.addWidget(self.property_list)
        top_layout.addWidget(self.value_field)
        top_panel.setLayout(top_layout)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.delete_button)
        bottom_panel.setLayout(bottom_layout)

        layout.addWidget(top_panel)
        layout.addWidget(bottom_panel)
        main_widget.setLayout(layout)
        self.main_layout.addWidget(main_widget)
        

class ColorBox(ControlPanelElement):
    def __init__(self, label_style, label_text, change_color_action, remove_color_action):
        super().__init__(label_style, label_text)
        self.setFixedHeight(180)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.color_label = QLabel(text="No color specified")
        self.color_label.setFont(QFont('Arial', 16))
        self.slider_color_r = ColorSlider()
        self.slider_color_g = ColorSlider()
        self.slider_color_b = ColorSlider()
        main_widget = QWidget()
        
        self.slider_color_r.valueChanged.connect(change_color_action)
        self.slider_color_g.valueChanged.connect(change_color_action)
        self.slider_color_b.valueChanged.connect(change_color_action)

        self.color_remove_button = QPushButton(text="Remove color")
        self.color_remove_button.clicked.connect(remove_color_action)

        layout.addWidget(self.color_label)
        layout.addWidget(self.slider_color_r)
        layout.addWidget(self.slider_color_g)
        layout.addWidget(self.slider_color_b)
        layout.addWidget(self.color_remove_button)

        main_widget.setLayout(layout)
        self.main_layout.addWidget(main_widget)

    def get_color_values(self):
        return (self.slider_color_r.value(), 
                self.slider_color_g.value(), 
                self.slider_color_b.value())

    def set_color_values(self, r, g, b):
        self.set_sliders_block_signals(True)
        self.slider_color_r.setValue(r)
        self.slider_color_g.setValue(g)
        self.slider_color_b.setValue(b)
        self.set_sliders_block_signals(False)

        hex_string = rgb_to_hex(r, g, b)
        self.set_color_label(f"Color: RGB ({r}, {g}, {b}) = {hex_string}")

    def set_color_label(self, text):
        self.color_label.setText(text)

    def set_sliders_hex(self, hex_string):
        r, g, b = hex_to_rgb(hex_string[1:])
        self.set_color_values(r, g, b)

    def set_sliders_block_signals(self, enabled):
        """
        Prevents sliders from triggering their functions when values change
        """
        self.slider_color_b.blockSignals(enabled)
        self.slider_color_g.blockSignals(enabled)
        self.slider_color_r.blockSignals(enabled)

    def set_sliders_enabled(self, enabled):
            """
            Enables or disables (and resets) color sliders when given True or False respectively
            """
            self.slider_color_r.setEnabled(enabled)
            self.slider_color_g.setEnabled(enabled)
            self.slider_color_b.setEnabled(enabled)
            
            self.reset_sliders()

    def reset_sliders(self):
        self.set_color_values(0, 0, 0)
        self.set_color_label(f"No color specified")

        
class ColorSlider(QSlider):
    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setSingleStep(1)
