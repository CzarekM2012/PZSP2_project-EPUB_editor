from os import listdir, mkdir, makedirs, unlink, walk, sep, remove
from os.path import relpath
from pathlib import Path
import zipfile
from zipfile import ZIP_DEFLATED, ZipFile
from shutil import rmtree, copyfile

from cssutils.css import CSSStyleDeclaration, CSSFontFaceRule
from gui_elements import *

import cssutils

from pathfinder import Pathfinder


class FileManager:
    FONT_MEDIA_TYPE = "application/x-font-ttf"

    def __init__(self):
        self.load_path = None
        self.css_files = []
        self.css_file_paths = []
        self.page_files_paths = []
        self.edition_dir = Path(__file__).parent / 'edit'
        self.pathfinder = Pathfinder(self.edition_dir)
        self.prepare_edition_dir()

    def prepare_edition_dir(self):
        if self.edition_dir.is_dir():
            for filename in listdir(self.edition_dir):
                file_path = self.edition_dir / filename
                try:
                    if file_path.is_file() or file_path.is_symlink():
                        unlink(file_path)
                    elif file_path.is_dir():
                        rmtree(file_path)
                except OSError as e:
                    # Probably only open file or lack of permissions
                    print(f'Failed to delete {file_path}. Reason: {e}')
            return
        mkdir(self.edition_dir)

    def load_book(self, file_path):
        """
        Unpacks a zip from specified path into the editing directory.
        Returns 0 if succeeded, or a positive number otherwise
        """
        self.load_path = Path(file_path)
        self.prepare_edition_dir()

        try:
            book = ZipFile(self.load_path)
            book.extractall(self.edition_dir)
            book.close()
        except PermissionError as e:
            print(f"Could not open file due to {e}")
            self.load_path = None
            self.css_files = []
            return 1
        except zipfile.BadZipFile as e:
            print(f"Could not open file due to {e}")
            self.load_path = None
            self.css_files = []
            return 2

        try:
            self.pathfinder.find_renditions()
            self.pathfinder.load_rendition()
        except Exception as e:
            print(f"Could not open file due to {e}")
            self.load_path = None
            self.css_files = []
            return 3

        self.page_files_paths, self.css_file_paths = \
            self.pathfinder.get_rendition_paths()

        self.load_css_files()

        print('File loaded')
        return 0

    def load_css_files(self):
        self.css_files = []
        for css_path in self.css_file_paths:
            self.css_files.append(cssutils.parseFile(css_path))

    # Saves changes by overwriting edited css files
    def update_css(self):
        for i in range(self.get_css_file_count()):
            css_file = open(self.css_file_paths[i], "wb")
            css_file.write(self.css_files[i].cssText)
            css_file.close()

    def is_file_loaded(self):
        return self.load_path is not None

    def get_css_param(self, style_name, param_name):
        style = self.get_css_style_by_name(style_name)
        if style is None:
            return ""

        return style.getPropertyValue(param_name)

    def set_css_param(self, style_name, param_name, value):
        style = self.get_css_style_by_name(style_name)
        if style is None:
            return
        style.setProperty(param_name, value)

    def remove_css_param(self, style_name, param_name):
        style = self.get_css_style_by_name(style_name)
        if style is None:
            return
        style.removeProperty(param_name)

    def get_css_file_paths(self):
        return [str(path) for path in self.css_file_paths]

    def get_css_style_names(self):
        name_list = []
        for file in self.css_files:
            for item in file.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                name_list.append(item.selectorText)
        return name_list

    def get_css_style_by_name(self, name):
        for file in self.css_files:
            for item in file.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                if name == item.selectorText:
                    return item.style
        return None

    def get_all_css_fonts(self):
        font_list = []
        for file in self.css_files:
            for item in file.cssRules.rulesOfType(cssutils.css.CSSRule.FONT_FACE_RULE):
                font_list.append(item.style)
        return font_list

    # Returns a list of string tuples: (name, value), one for each parameter
    def get_css_params_by_style_name(self, name):
        param_list = []
        style = self.get_css_style_by_name(name)
        if style is None:
            return param_list

        for property in style.getProperties():
            param_list.append((property.name, property.value))
        return param_list

    def get_css_file(self, file_index):
        return self.css_files[file_index]

    def get_css_file_by_path(self, file_path):
        if file_path is not None:
            file_path = Path(file_path)
        for i in range(len(self.css_files)):
            if self.css_file_paths[i] == file_path:
                return self.css_files[i]

    def get_css_text(self, file_index):
        return str(self.css_files[file_index].cssText, 'utf-8')

    def overwrite_css_file_with_text(self, file_path, text):

        # Manually overwrite specified file
        try:
            css_file = open(file_path, "w")
            css_file.write(text)
            css_file.close()
        except FileNotFoundError as e:
            print(f"Could not save CSS file due to {e}")

        # Reload all CSS files
        self.load_css_files()

    def set_css_file_by_path(self, file_path):
        for i in range(len(self.css_files)):
            if self.css_file_paths[i] == file_path:
                return self.css_files[i]

    def get_css_text_by_path(self, file_path):
        stylesheet = self.get_css_file_by_path(file_path)
        if stylesheet is None:
            return ""
        return str(stylesheet.cssText, 'utf-8')

    def get_css_file_count(self):
        return len(self.css_files)

    def save_book(self, file_path):

        save_path = Path(file_path).resolve()
        self.update_css()
        self.pathfinder.save_rendition_file()

        # folder_name = path.splitext(path.basename(save_path))[0]
        # will get permission error if there is a folder with name "folder_name"
        # in save_dir
        try:
            book = ZipFile(save_path, 'w', ZIP_DEFLATED)

            for root, dirs, files in walk(self.edition_dir):
                for file in files:
                    file_path = Path(root) / file
                    book.write(file_path,
                               file_path.relative_to(self.edition_dir))
            book.close()
        except PermissionError as e:
            print(f"Could not save file due to {e}")
            return

        print('File saved')

    def get_page(self, page_nr):

        # Because later checks still return index 0, if there are 0 pages
        if self.get_page_count() == 0:
            return 0, None

        # Check if requested page number is correct
        if page_nr < 0:
            page_nr = self.get_page_count() - 1
        elif page_nr >= self.get_page_count():
            page_nr = 0

        page_file_path = self.edition_dir / self.page_files_paths[page_nr]

        # Also return page nr, because it can change
        return page_nr, QUrl.fromLocalFile(page_file_path)

    def get_page_count(self):
        return len(self.page_files_paths)

    def add_font_file(self, file_path):
        path_obj = Path(file_path)

        file_name = path_obj.name
        if '.' in file_name:
            file_name = file_name.split('.', 1)[0]

        new_path = self.edition_dir / self.pathfinder.get_font_folder_path() / path_obj.name
        makedirs(new_path.parent, exist_ok=True)
        copyfile(file_path, new_path)

        attributes = [
            "font_" + file_name,
            new_path,
            self.FONT_MEDIA_TYPE
        ]
        self.pathfinder.add_item_to_rendition_manifest(attributes)

        return new_path

    def remove_font_file(self, file_path):
        path_obj = Path(file_path)

        file_name = path_obj.name
        if '.' in file_name:
            file_name = file_name.split('.', 1)[0]

        new_path = self.edition_dir / self.pathfinder.get_font_folder_path() / path_obj.name
        try:
            remove(Path(new_path).resolve())
        except FileNotFoundError as e:
            print(e)

        attributes = [
            "font_" + file_name,
            new_path
        ]
        self.pathfinder.remove_item_from_rendition_manifest(attributes)

    def add_font_to_epub(self, font):
        new_path = self.add_font_file(font.file_path)
        self.add_css_font_property(font, new_path)

    def remove_font_from_epub(self, font):
        self.remove_font_file(font.file_path)
        self.remove_css_font_property(font)
        pass

    def add_css_font_property(self, font, book_relative_path):
        font_list = self.get_all_css_fonts()

        # Check if such property already exists
        for css_font in font_list:
            font_family = css_font.getProperties('font-family')[0].propertyValue.cssText
            if font_family == font.name:
                return

        # Add this to any CSS file
        css_relative_path = relpath(book_relative_path, self.css_file_paths[0].parent)
        font_path = css_relative_path.replace(sep, '/')
        font_style = CSSStyleDeclaration()
        font_style.setProperty('font-family', value=font.name)
        font_style.setProperty('src', value=f'url("{font_path}")')
        self.css_files[0].add(CSSFontFaceRule(style=font_style))

    def remove_css_font_property(self, font):
        for file in self.css_files:
            for index, rule in enumerate(file.cssRules):
                if type(rule) == CSSFontFaceRule and rule.style.getProperties('font-family')[0].propertyValue.cssText \
                        == font.name:
                    file.deleteRule(index)
                    pass

    def get_used_font_name_list(self):
        font_list = []
        for file in self.css_files:
            for rule in file.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                props = rule.style.getProperties('font-family')
                if len(props) < 1:
                    continue

                font_text = props[0].propertyValue.cssText
                if ',' in font_text:
                    font_text = font_text.split(',', 1)[0]

                if font_text not in font_list:
                    font_list.append(font_text)

        return font_list

    def get_css_font_name_list(self):
        font_list = []
        for file in self.css_files:
            for item in file.cssRules.rulesOfType(cssutils.css.CSSRule.FONT_FACE_RULE):
                font_list.append(item.style.getProperties('font-family')[0].propertyValue.cssText)
        return font_list
