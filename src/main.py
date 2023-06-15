from PyQt6.QtWidgets import QApplication
from app.controllers.MainWindow_controller import MainWindowController

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.show()
    sys.exit(app.exec())