import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.SettingsMenu_ui import Ui_SettingsMenu


class SettingsMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.debugBtn.clicked.connect(self.toggle_debug)
        self.ui.debugBtn.setText("Disable debug mode")

    def toggle_debug(self):
        root_logger = logging.getLogger()
        if root_logger.level == logging.DEBUG:
            root_logger.setLevel(logging.INFO)
            self.ui.debugBtn.setText("Enable debug mode")
        else:
            root_logger.setLevel(logging.DEBUG)
            self.ui.debugBtn.setText("Disable debug mode")
