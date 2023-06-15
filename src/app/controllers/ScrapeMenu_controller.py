from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu

class ScrapeMenuController(QWidget):
    back_btn_clicked = pyqtSignal()
    submit_scrape = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.ui.backBtn.clicked.connect(self.handle_back_btn_clicked)
        self.ui.submitBtn.clicked.connect(self.handle_scrape_submission)

    def handle_back_btn_clicked(self):
        self.back_btn_clicked.emit()

    def handle_scrape_submission(self):
        self.submit_scrape.emit()