from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.SettingsMenu_ui import Ui_SettingsMenu


class SettingsMenuController(QWidget):
    back_btn_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsMenu()
        self.ui.setupUi(self)

        self.ui.backBtn.clicked.connect(self.handle_back_btn_clicked)

    def handle_back_btn_clicked(self):
        self.back_btn_clicked.emit()
