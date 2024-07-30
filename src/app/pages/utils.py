import os
import sys
from subprocess import Popen, PIPE, STDOUT

from PyQt6.QtWidgets import QMessageBox


def open_file(path, self):
    """Platform-independent os.startfile()"""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            Popen([opener, path], stderr=STDOUT, stdout=PIPE)
    except Exception as e:
        exc_msg = f"Could not open path '{path}': {e}"
        self._logger.error(exc_msg)
        QMessageBox.critical(self, "Failed to open", exc_msg)
