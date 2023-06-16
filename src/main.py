from PyQt6.QtWidgets import QApplication
from app.controllers.MainWindow_controller import MainWindowController
from app.logger_utils.log_handler import QtLogHandler
import logging
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_handler = QtLogHandler()
    logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])
    window = MainWindowController(log_handler)
    window.show()
    sys.exit(app.exec())