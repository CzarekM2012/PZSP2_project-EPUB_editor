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

    #file_path = path.join(base_path, 'books', 'niezwyciezony.epub')

    file_path = path.join(base_path, 'books', 'niezwyciężony', 'OEBPS', 'Text', 'index_split_003.html')
    start_app(file_path)


if __name__ == '__main__':
    main()