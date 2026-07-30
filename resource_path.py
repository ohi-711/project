import os
import sys


def resource_path(relative_path):
    """
    Resolve a path to a bundled resource (image, gif, font, etc.) so it
    works both when running from source (`python main.py`) and when running
    from a PyInstaller-built exe.

    PyInstaller unpacks bundled data files (added via --add-data) into a
    temporary folder and exposes that folder's path as sys._MEIPASS at
    runtime. When that attribute doesn't exist, we're running from source,
    so we just fall back to the current working directory.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)