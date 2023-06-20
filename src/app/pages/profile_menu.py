import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.ProfileMenu_ui import Ui_ProfileMenu


class ProfileMenu(QWidget):
    open_profile = pyqtSignal()
    back = pyqtSignal()
    rescrape = pyqtSignal(str, str, int, int)
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProfileMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.rescrapeBtn.clicked.connect(self.handle_rescrape)
        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.openBtn.clicked.connect(self.open_profile.emit)

    def handle_rescrape(self):
        self.rescrape.emit("Chevrolet", "Corvette", 2005, 2007)
