from PySide6.QtWidgets import QApplication

# Only needed for access to command line arguments
import sys
import os
from pathlib import Path
from main_window import MainWindow
from qt_material import apply_stylesheet

debug = False
folder_name = Path(__file__).parent.name
if folder_name == "pzsp2":
    debug = True


def start_app():
    app = QApplication(sys.argv)
    screen_size = app.primaryScreen().availableGeometry().size()
    apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow(screen_size)
    window.show()

    app.exec()


def main():
    global debug
    base_path = Path(__file__).parent

    if not debug:
        base_path = Path(base_path).parent

    os.chdir(base_path)

    start_app()


if __name__ == '__main__':
    main()
