from PySide6.QtWidgets import QApplication, QWidget  # type:ignore
from PySide6.QtWebEngineWidgets import QWebEngineView  # type:ignore
from PySide6.QtCore import QByteArray, QUrl  # type:ignore
from PySide6.QtWebEngineQuick import QtWebEngineQuick  # type:ignore

# Only needed for access to command line arguments
import sys
import os.path as path


def start_app(file_path, base_path):
    app = QApplication(sys.argv)
    window = QWebEngineView()
    with open(file_path, encoding='utf-8') as file:
        page_data = file.readlines()
    page_data = ''.join(page_data)
    page_data = QByteArray(page_data.encode())
    window.setContent(page_data, mimeType="text/html;charset=UTF-8", baseUrl=QUrl.fromLocalFile(base_path))
    window.show()

    app.exec()


if __name__ == '__main__':
    filePath1 = 'resources/html/common_tasks.xhtml'
    basePath1 = path.dirname(__file__) + '/'
    fp2 = 'books/pantadeusz/nav.xhtml'
    bp2 = basePath1 + 'books/pantadeusz/'

    start_app(fp2, bp2)
