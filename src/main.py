import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from app.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    thread = QThread()
    main_window.req_handler.moveToThread(thread)
    thread.started.connect(main_window.req_handler.start)
    thread.start()

    main_window.show()
    sys.exit(app.exec())