from ebooklib import epub
import ebooklib


class Reader:
    def __init__(self, file_path: str) -> None:
        self.read(file_path)

    def read(self, file_path) -> None:
        self.book = epub.read_epub(file_path)

    def get_page_count(self) -> int:
        return len(self.book.spine)

    def get_page_content(self, page_number) -> bytes:
        page_id = self.book.spine[page_number][0]
        page = self.book.get_item_with_id(page_id)
        return page.content

    # Compiles a big stylesheet containing all CSS files of .epub file

    def get_stylesheet(self) -> bytes:
        stylesheets = self.book.get_items_of_type(ebooklib.ITEM_STYLE)
        complete_stylesheet = b''
        for stylesheet in stylesheets:
            complete_stylesheet += stylesheet.content
        return complete_stylesheet
