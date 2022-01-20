from pathlib import Path

from cssutils import css
class Font:
    TYPE_NO_FILE = 0
    TYPE_LOCAL_FILE = 1
    TYPE_FROM_EPUB = 2
    TYPE_UNKNOWN = 3

    def __init__(self, name, file_type=0, fallback=None):
        
        self.name = name
        self.fallback = fallback
        self.file_path = None
        self.file_type = file_type
        
        if fallback == None:
            self.fallback = self.guess_font_family(name)
        else:
            self.fallback = fallback

        if '.' not in name:
            self.name = name

            # No valid local file found
            if file_type == self.TYPE_LOCAL_FILE:
                self.file_type = self.TYPE_NO_FILE
            return

        self.file_path = name
        path = Path(name)
        self.name = path.name.split('.', 1)[0]     # Override name, if it's a path
        extension = path.name.rsplit('.', 1)[1]
        
        # Check if file is of correct type
        if file_type != self.TYPE_NO_FILE and extension.lower() == 'ttf':
            self.file_path = name
        else: # No valid local file found
            self.file_path = None
            self.file_type = self.TYPE_NO_FILE

    @staticmethod
    def guess_font_family(font_name):
        font_family = 'sans-serif'
        if "monospace" in font_name:
            font_family = "monospace"
        elif "cursive" in font_name:
            font_family = "cursive"
        elif "serif" in font_name and "sans" not in font_name:
            font_family = 'serif'
        return font_family

    @staticmethod
    def get_font_from_css_string(css_string):
        font_name = css_string
        fallback_font = ''
        if ',' in css_string:
            font_name = css_string.split(',')[0]
            if font_name[0] == "'" or font_name[0] == '"':
                font_name = font_name[1:-1]
            
            fallback_font = css_string.split(',', 1)[1].strip()
        
        if fallback_font == '':
            fallback_font = Font.guess_font_family(css_string)

        return Font(font_name, file_type=Font.TYPE_UNKNOWN, fallback=fallback_font)

    def __str__(self):
        type_str = ""
        if self.file_type == self.TYPE_NO_FILE:
            type_str = ' [Basic] '
        elif self.file_type == self.TYPE_LOCAL_FILE:
            type_str = '[Local] '
        elif self.file_type == self.TYPE_FROM_EPUB:
            type_str = '  [EPUB] '
        
        file_string = ''
        #if self.file_type == self.TYPE_LOCAL_FILE:
        #    file_string = ' from: ' + self.file_path

        return f"{type_str}{self.name} ({self.fallback}){file_string}"

