import logging
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path


def open_path(path: Path) -> bool:
    """Platform-independent method to open a file or program with the default application.

    Args:
        path (Path): The file or program to open. 
    
    Returns:
        bool: True if the file/program was opened successfully, False otherwise.
    """
    try:
        if sys.platform == "win32":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            Popen([opener, path], stderr=STDOUT, stdout=PIPE)
    except Exception as e:
        logging.getLogger(__file__).error(f"Could not open path '{path}': {e}")
        return False


def remove_path(path: Path) -> bool:
    """Removes a directory if it exists and is empty.

    Args:
        path (Path): The directory to remove.

    Returns:
        bool: True if the path was removed successfully, False otherwise.
    """
    try:
        Path.rmdir(path)
    except OSError as e:
        logging.error(f"Could not remove directory '{path}': {e}")
        return False
