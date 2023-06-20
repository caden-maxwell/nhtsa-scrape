import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QDialog

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.ui.LoadingDialog_ui import Ui_LoadingDialog


class ScrapeMenu(QWidget):
    back = pyqtSignal()
    scrape_finished = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)
        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submission)

        self.ui.startYearCombo.addItem("Any")
        self.ui.endYearCombo.addItem("Any")
        self.ui.startYearCombo.addItems([str(year) for year in range(2004, 2017)])
        self.ui.endYearCombo.addItems([str(year) for year in range(2004, 2017)])

        self.logger = logging.getLogger(__name__)

        self.loading_window = LoadingWindow()

    def handle_submission(self):
        self.loading_window.show()

    def setup(self, make="All", model="All", start_year="Any", end_year="Any"):
        self.ui.makeEdit.setText(make)
        self.ui.modelEdit.setText(model)
        self.ui.startYearCombo.setCurrentText(str(start_year))
        self.ui.endYearCombo.setCurrentText(str(end_year))
    

class LoadingWindow(QDialog):
    cancel_btn_clicked = pyqtSignal()
    view_btn_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoadingDialog()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.cancel_button = self.ui.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.view_button = self.ui.buttonBox.addButton("View", QDialogButtonBox.ButtonRole.AcceptRole)
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
