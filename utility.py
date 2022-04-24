from PySide6.QtWidgets import QMessageBox


font_list_built_in = [
    ("Arial", "sans-serif"),
    ("Verdana", "sans-serif"),
    ("Helvetica", "sans-serif"),
    ("Tahoma", "sans-serif"),
    ("Trebuchet MS", "sans-serif"),
    ("Times New Roman", "serif"),
    ("Georgia", "serif"),
    ("Garamond", "serif"),
    ("Courier New", "monospace"),
    ("Brush Script MT", "cursive"),
]


def rgb_to_hex(r, g, b):
    """
    Takes values from range 0-255 and returns a hex string in format "RRGGBB"
    """
    return '#%02x%02x%02x' % (r, g, b)


def hex_to_rgb(hex_string):
    """
    String has to be formatted this way: "RRGGBB" or "RGB" (shorthand version)
    Returns a tuple of integers like (R, G, B), where each value is in range 0-255
    """

    if len(hex_string) == 6:                # Classic hex string
        r = int("0x" + hex_string[:2], 0)
        g = int("0x" + hex_string[2:4], 0)
        b = int("0x" + hex_string[4:], 0)
    elif len(hex_string) == 3:              # Shorthand hex string
        r = int("0x" + hex_string[0] + hex_string[0], 0)
        g = int("0x" + hex_string[1] + hex_string[1], 0)
        b = int("0x" + hex_string[2] + hex_string[2], 0)
    else:                                  # Not a valid hex string
        return None
    return r, g, b


def file_open_error():
    error = QMessageBox()
    error.setText("ERROR - could not open file. Not a valid EPUB.")
    error.setWindowTitle("Error")
    error.exec()
