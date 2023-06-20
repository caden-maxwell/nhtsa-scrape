from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
import sys, os

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())