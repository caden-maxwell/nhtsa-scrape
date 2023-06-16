from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.ProfileMenu_ui import Ui_ProfileMenu


class ProfileMenuWidget(QWidget):
    open_profile_clicked = pyqtSignal()
    back_button_clicked = pyqtSignal()
    rescrape_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.ui.rescrapeBtn.clicked.connect(self.rescrape_clicked.emit)
        self.ui.backBtn.clicked.connect(self.back_button_clicked.emit)
        self.ui.openBtn.clicked.connect(self.open_profile_clicked.emit)
