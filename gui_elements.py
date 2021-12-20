from PySide6.QtCore import QUrl, Qt
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QMenuBar, QSlider, QTextEdit, QVBoxLayout, QWidget


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
