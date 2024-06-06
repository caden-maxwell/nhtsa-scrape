import sys

from PyQt6.QtWidgets import QApplication

from app.main_window import MainWindow
import matplotlib
matplotlib.use('qtagg')

try:
    import pyi_splash
except Exception:
    pass

if __name__ == "__main__":
    try:
        pyi_splash.close()
    except Exception:
        pass

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
