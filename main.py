from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtWebEngineQuick import QtWebEngineQuick

# Only needed for access to command line arguments
import sys


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
    file_path1 = 'resources/html/common_tasks.xhtml'
    base_path1 = 'D:/Code/Python/PZSP2/pysideTest/resources/html/'
    fp2 = 'pantadeusz/nav.xhtml'
    bp2 = 'D:/Code/Python/PZSP2/pysideTest/pantadeusz/'

    start_app(fp2, bp2)
