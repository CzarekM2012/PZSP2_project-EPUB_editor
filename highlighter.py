from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
import re


class Highlighter(QSyntaxHighlighter):
    def __init__(self, document=None):
        super().__init__(document)

        self._mappings = {}

    def add_mapping(self, pattern, format):
        self._mappings[pattern] = format

    def highlightBlock(self, text):
        for pattern, format in self._mappings.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

    def setup(self):
        value_format = QTextCharFormat()
        value_format.setFontItalic(True)
        value_format.setForeground(QColor("cyan"))
        pattern = r':\s*.*;*$'
        self.add_mapping(pattern, value_format)

        property_format = QTextCharFormat()
        property_format.setFontWeight(QFont.Bold)
        property_format.setForeground(QColor("orange"))
        pattern = r'^\s*.*:'
        self.add_mapping(pattern, property_format)

        selector_format = QTextCharFormat()
        selector_format.setFontWeight(QFont.Bold)
        selector_format.setForeground(QColor("magenta"))
        pattern = r'^\s*.*{'
        self.add_mapping(pattern, selector_format)

        punctuation_format = QTextCharFormat()
        pattern = r'[;:{}]'
        punctuation_format.setForeground(QColor("white"))
        self.add_mapping(pattern, punctuation_format)
