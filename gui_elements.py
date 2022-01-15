from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QFont
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QMenuBar, QSlider, QTextEdit, QVBoxLayout, QWidget, QLabel, QPushButton
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


class ColorBox(QWidget):
    def __init__(self, change_color_action, remove_color_action):
        super().__init__()
        layout = QVBoxLayout()
        self.color_label = QLabel(text="No color specified")
        self.color_label.setFont(QFont('Arial', 20))
        self.slider_color_r = ColorSlider()
        self.slider_color_g = ColorSlider()
        self.slider_color_b = ColorSlider()
        
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

        self.setLayout(layout)
        self.setFixedHeight(170)

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
