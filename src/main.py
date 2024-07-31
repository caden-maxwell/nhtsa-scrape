import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QIcon

from app.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    icon_path = Path(__file__).parent / "app" / "resources" / "icon.png"
    pixmap = QPixmap()
    pixmap.loadFromData(icon_path.read_bytes())
    appIcon = QIcon(pixmap)
    app.setWindowIcon(appIcon)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
