from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu


class ScrapeMenuWidget(QWidget):
    back_button_clicked = pyqtSignal()
    submit_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.ui.backBtn.clicked.connect(self.back_button_clicked.emit)
        self.ui.submitBtn.clicked.connect(self.submit_button_clicked.emit)
