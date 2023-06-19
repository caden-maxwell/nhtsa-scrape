import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QDialog

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class ScrapeMenuController(QWidget):
    back_button_clicked = pyqtSignal()
    scrape_finished = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.ui.backBtn.clicked.connect(self.back_button_clicked.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submission)

        self.loading_window_controller = LoadingWindowController()

    def handle_submission(self):
        self.loading_window_controller.show()
    

class LoadingWindowController(QDialog):
    cancel_btn_clicked = pyqtSignal()
    view_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        view_button = self.ui.buttonBox.addButton("View", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button.clicked.connect(self.handle_cancel_button_clicked)
        view_button.clicked.connect(self.handle_view_button_clicked)

    def show(self):
        self.exec()

    def handle_cancel_button_clicked(self):
        self.logger.info("Cancel button clicked")
        self.close()

    def handle_view_button_clicked(self):
        ### TODO: Add logic to get scraped data and export to data viewer ###
        self.logger.info("View button clicked")
        self.close()