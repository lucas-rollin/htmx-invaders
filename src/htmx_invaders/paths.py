"""Filesystem locations for bundled assets."""

import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


FONT_PATH = resource_path(os.path.join("assets", "fonts", "SpaceMono-Regular.ttf"))
IMG_DIR = resource_path(os.path.join("assets", "img"))
SFX_DIR = resource_path(os.path.join("assets", "sfx"))
