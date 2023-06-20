import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QDialog

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.ui.LoadingDialog_ui import Ui_LoadingDialog

from . import DataView


class ScrapeMenu(QWidget):
    back = pyqtSignal()

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
        self.profile_id = -1

        self.loading_window = LoadingWindow()
        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

    def handle_submission(self):
        self.loading_window.show()

    def setup(self, profile_id=-1, make="All", model="All", start_year="Any", end_year="Any"):
        self.profile_id = profile_id
        self.ui.makeEdit.setText(make)
        self.ui.modelEdit.setText(model)
        self.ui.startYearCombo.setCurrentText(str(start_year))
        self.ui.endYearCombo.setCurrentText(str(end_year))

    def open_data_viewer(self):
        self.data_viewer = DataView(self.is_new_profile())
        self.data_viewer.show()

    def is_new_profile(self):
        return self.profile_id < 0
    

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
        self.view_btn_clicked.emit()
