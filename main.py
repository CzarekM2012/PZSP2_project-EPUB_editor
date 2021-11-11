from PySide6.QtWidgets import QApplication, QStyleFactory

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


def start_app():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow()
    window.show()
    
    app.exec()


def main():
    global debug
    base_path = path.dirname(__file__)

    if not debug:
        base_path = os.path.split(base_path)[0]

    # Just in case
    os.chdir(base_path)

    start_app()


if __name__ == '__main__':
    main()