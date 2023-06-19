from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.MainMenu_ui import Ui_MainMenu


class MainMenu(QWidget):
    new_scrape_clicked = pyqtSignal()
    open_existing_clicked = pyqtSignal()
    logs_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainMenu()
        self.ui.setupUi(self)

        self.ui.scrapeBtn.clicked.connect(self.new_scrape_clicked.emit)
        self.ui.openBtn.clicked.connect(self.open_existing_clicked.emit)
        self.ui.logsBtn.clicked.connect(self.logs_clicked.emit)
        self.ui.settingsBtn.clicked.connect(self.settings_clicked.emit)