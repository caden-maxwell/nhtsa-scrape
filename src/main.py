import sys

from PyQt6.QtWidgets import QApplication

from app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("windows11")

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
