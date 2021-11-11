from os import path, listdir, mkdir, unlink, walk
import zipfile
from zipfile import ZIP_DEFLATED, ZipFile
from shutil import rmtree
from gui_elements import *

import cssutils

from pathfinder import Pathfinder

class FileManager:

    def __init__(self):
        self.stylesheet_text = None
        self.edition_dir = path.join(path.dirname(__file__), 'edit')
        self.pathfinder = Pathfinder(self.edition_dir)

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
        self.load_path = path.abspath(file_path)
        self.prepare_edition_dir()
        book = ZipFile(self.load_path)
        book.extractall(self.edition_dir)
        book.close()
        
        self.pathfinder.search()
        css_file_paths = self.pathfinder.get_css_path_list()
        css_files = []
        for i in range(len(css_file_paths)):
            css_files.append(cssutils.parseFile(css_file_paths[i]))
        print(css_files)

        for item in css_files[1].cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
            item.style.setProperty("color", "#00ff00")
            #for property in item.style.getProperties():
                #if property.name == "color":
                #    property.value = "#00ff00"

        for item in css_files[1].cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
            for property in item.style.getProperties():
                print(property)

        print(css_files[1].cssText)

        css_file = open(css_file_paths[1], "wb")
        css_file.write(css_files[1].cssText)

        print('File loaded')


    def load_css(self):
        css_file_path = path.join(self.edition_dir,
                                  self.pathfinder.stylesheets[0])
        with open(css_file_path) as file:
            self.stylesheet_text = ''.join(file.readlines())

    def get_stylesheet_text(self):
        if self.stylesheet_text == None:
            self.load_css()
        
        return self.stylesheet_text


    def save_book(self, file_path):

        self.save_path = path.abspath(file_path)

        # folder_name = path.splitext(path.basename(save_path))[0]
        # will get permission error if there is a folder with name "folder_name"
        # in save_dir
        book = ZipFile(self.save_path, 'w', ZIP_DEFLATED)
        for root, dirs, files in walk(self.edition_dir):
            for file in files:
                book.write(path.join(root, file),
                           path.relpath(path.join(root, file),
                           self.edition_dir))
        book.close()
        print('File saved')

    
    def get_page(self, page_nr):

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
