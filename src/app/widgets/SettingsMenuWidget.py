from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.SettingsMenu_ui import Ui_SettingsMenu


class SettingsMenuWidget(QWidget):
    back_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self.ui.backBtn.clicked.connect(self.back_button_clicked.emit)
