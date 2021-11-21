from os import path, listdir, mkdir, unlink, walk
import zipfile
from zipfile import ZIP_DEFLATED, ZipFile
from shutil import rmtree

from cssutils.css.cssstylesheet import CSSStyleSheet
from gui_elements import *

import cssutils

from pathfinder import Pathfinder

class FileManager:

    def __init__(self):
        self.load_path = None
        self.css_files = []
        self.edition_dir = path.join(path.dirname(__file__), 'edit')
        self.pathfinder = Pathfinder(self.edition_dir)
        self.prepare_edition_dir()

    def prepare_edition_dir(self):
        if path.isdir(self.edition_dir):
            for filename in listdir(self.edition_dir):
                file_path = path.join(self.edition_dir, filename)
                try:
                    if path.isfile(file_path) or path.islink(file_path):
                        unlink(file_path)
                    elif path.isdir(file_path):
                        rmtree(file_path)
                except OSError as e:
                    # Probably only open file or lack of permissions
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            mkdir(self.edition_dir)

    def load_book(self, file_path):
        """
        Unpacks a zip from specified path into the editing directory.
        Returns 0 if succeded, or a positive number otherwise
        """
        self.load_path = path.abspath(file_path)
        self.prepare_edition_dir()

        try:
            book = ZipFile(self.load_path)
            book.extractall(self.edition_dir)
            book.close()
        except PermissionError as e:
            print(f"Could not open file due to {e}")
            self.load_path = None
            self.css_files = []
            self.pathfinder = Pathfinder(self.edition_dir)
            return 1

        try:
            self.pathfinder.search()
        except Exception as e:
            print(f"Could not open file due to {e}")
            self.load_path = None
            self.css_files = []
            self.pathfinder = Pathfinder(self.edition_dir)
            return 2

        self.css_file_paths = self.pathfinder.get_css_path_list()
        
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
        return not self.load_path == None

    def get_css_param(self, style_name, param_name):
        style = self.get_css_style_by_name(style_name)
        if style == None:
            return
        
        return style.getPropertyValue(param_name)


    def set_css_param(self, style_name, param_name, value):
        style = self.get_css_style_by_name(style_name)
        if style == None:
            return
        #print(f"Param name: {param_name}, Value: {value}")
        style.setProperty(param_name, value)

    def remove_css_param(self, style_name, param_name):
        style = self.get_css_style_by_name(style_name)
        if style == None:
            return
        style.removeProperty(param_name)


    def get_css_file_paths(self):
        return self.css_file_paths


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

    
    # Returns a list of string tuples: (name, value), one for each parameter
    def get_css_params_by_style_name(self, name):
        param_list = []
        style = self.get_css_style_by_name(name)
        if style == None:
            return param_list
        
        for property in style.getProperties():
            param_list.append((property.name, property.value))
        return param_list


    def get_css_file(self, file_index):
        return self.css_files[file_index]


    def get_css_file_by_path(self, file_path):
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

        #file = self.get_stylesheet_file_by_path(file_path)
        #if file == None:
        #    return
        
        #print(text)
        #file.setCSSText(bytes(text, 'utf-8')) #TODO: Check encoding, probably need binary


    def set_css_file_by_path(self, file_path, css_file):
        for i in range(len(self.css_files)):
            if self.css_file_paths[i] == file_path:
                return self.css_files[i]


    def get_css_text_by_path(self, file_path):
        stylesheet = self.get_css_file_by_path(file_path)
        if stylesheet == None:
            return ""
        return str(stylesheet.cssText, 'utf-8')
        

    def get_css_file_count(self):
        return len(self.css_files)


    def save_book(self, file_path):

        save_path = path.abspath(file_path)
        self.update_css()

        # folder_name = path.splitext(path.basename(save_path))[0]
        # will get permission error if there is a folder with name "folder_name"
        # in save_dir
        try:
            book = ZipFile(save_path, 'w', ZIP_DEFLATED)

            for root, dirs, files in walk(self.edition_dir):
                for file in files:
                    book.write(path.join(root, file),
                               path.relpath(path.join(root, file),
                               self.edition_dir))
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
           page_nr = self.get_page_count()-1
        elif page_nr >= self.get_page_count():
            page_nr = 0

        page_file_path = path.join(self.edition_dir,
                                   self.pathfinder.spine[page_nr])
        
        # Also return page nr, because it can change
        return page_nr, QUrl.fromLocalFile(page_file_path)
    
    
    def get_page_count(self):
        return self.pathfinder.get_html_doc_count()
