import logging

from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class LoadingWindow(QDialog):
    cancel_btn_clicked = pyqtSignal()
    view_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.view_button = self.ui.buttonBox.addButton("View Data", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_button.clicked.connect(self.handle_cancel_button_clicked)
        self.view_button.clicked.connect(self.handle_view_button_clicked)

    def show(self):
        self.exec()

    def handle_cancel_button_clicked(self):
        self.logger.info("Scrape cancelled, data not saved.")
        self.close()

    def handle_view_button_clicked(self):
        ### TODO: Add logic to stop scraping data and export everything to the data viewer ###
        self.logger.info("Scraping stopped and data viewer opened.")
        self.close()
        self.view_btn_clicked.emit()