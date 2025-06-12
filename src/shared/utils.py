import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller-built .exe
    """
    try:
        # If running as a bundled app
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except AttributeError:
        # If running as a script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)