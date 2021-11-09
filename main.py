from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory, QWidget  # type:ignore
from PySide6.QtWebEngineWidgets import QWebEngineView  # type:ignore
from PySide6.QtCore import QByteArray, QUrl  # type:ignore
from PySide6.QtWebEngineQuick import QtWebEngineQuick  # type:ignore

# Only needed for access to command line arguments
import sys
import os
import os.path as path
from main_window import MainWindow
from qt_material import apply_stylesheet

debug = False
folder_name = path.split(path.dirname(__file__))[1]
if(folder_name == "pzsp2"):
    debug = True

def start_app(file_path):
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow(file_path)
    window.show()
    app.exec()


def main():
    global debug
    base_path = path.dirname(__file__)

    if not debug:
        base_path = os.path.split(base_path)[0]
    
    # Just in case
    os.chdir(base_path)

    nav_path = path.join(base_path, 'books', 'pantadeusz', 'nav.xhtml')
    start_app(nav_path)


if __name__ == '__main__':
    main()