from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.MainMenu_ui import Ui_MainMenu


class MainMenuController(QWidget):
    new_scrape_clicked = pyqtSignal()
    open_existing_clicked = pyqtSignal()
    logs_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainMenu()
        self.ui.setupUi(self)

        self.ui.scrapeBtn.clicked.connect(self.handle_new_scrape_clicked)
        self.ui.openBtn.clicked.connect(self.handle_open_existing_clicked)
        self.ui.logsBtn.clicked.connect(self.handle_logs_clicked)
        self.ui.settingsBtn.clicked.connect(self.handle_settings_clicked)

    def handle_new_scrape_clicked(self):
        self.new_scrape_clicked.emit()

    def handle_open_existing_clicked(self):
        self.open_existing_clicked.emit()

    def handle_logs_clicked(self):
        self.logs_clicked.emit()

    def handle_settings_clicked(self):
        self.settings_clicked.emit()
