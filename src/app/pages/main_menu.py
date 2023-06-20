from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from app.ui.MainMenu_ui import Ui_MainMenu


class MainMenu(QWidget):
    new = pyqtSignal()
    existing = pyqtSignal()
    logs = pyqtSignal()
    settings = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainMenu()
        self.ui.setupUi(self)

        self.ui.scrapeBtn.clicked.connect(self.new.emit)
        self.ui.openBtn.clicked.connect(self.existing.emit)
        self.ui.logsBtn.clicked.connect(self.logs.emit)
        self.ui.settingsBtn.clicked.connect(self.settings.emit)
