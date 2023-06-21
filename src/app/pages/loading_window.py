import logging
from PyQt6 import QtGui

from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class LoadingWindow(QDialog):
    view_btn_clicked = pyqtSignal()
    
    def __init__(self, scrape_engine):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)
        self.scrape_engine = scrape_engine

        self.logger = logging.getLogger(__name__)

        self.cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.view_button = self.ui.buttonBox.addButton("Stop and View Data", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_button.clicked.connect(self.handle_cancel_clicked)
        self.view_button.clicked.connect(self.handle_view_clicked)

    def handle_cancel_clicked(self):
        self.logger.info("Scrape cancelled, all scraped data discarded.")
        self.scrape_engine.terminate()

    def handle_view_clicked(self):
        ### TODO: Add logic to stop scraping data and export everything to the data viewer ###
        self.logger.info("Data viewer opened.")
        self.close()
        self.view_btn_clicked.emit()

    def closeEvent(self, a0):
        self.handle_cancel_clicked()
        return super().closeEvent(a0)