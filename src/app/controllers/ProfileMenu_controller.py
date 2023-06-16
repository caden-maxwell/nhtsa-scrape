from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from app.ui.ProfileMenu_ui import Ui_ProfileMenu


class ProfileMenuController(QWidget):
    open_profile_clicked = pyqtSignal()
    back_btn_clicked = pyqtSignal()
    rescrape_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.ui.rescrapeBtn.clicked.connect(self.handle_rescrape_clicked)
        self.ui.backBtn.clicked.connect(self.handle_back_btn_clicked)
        self.ui.openBtn.clicked.connect(self.handle_open_profile_clicked)

    def handle_back_btn_clicked(self):
        self.back_btn_clicked.emit()

    def handle_open_profile_clicked(self):
        self.open_profile_clicked.emit()
    
    def handle_rescrape_clicked(self):
        self.rescrape_clicked.emit()