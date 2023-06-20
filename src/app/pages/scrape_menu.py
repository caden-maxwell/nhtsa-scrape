import logging
from time import sleep

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialogButtonBox, QDialog
from bs4 import BeautifulSoup

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.ui.LoadingDialog_ui import Ui_LoadingDialog

from . import DataView
from app.scrape import SearchScrape


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)
        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.refreshBtn.clicked.connect(self.handle_refresh)
        self.ui.submitBtn.clicked.connect(self.handle_submission)

        self.handle_refresh()

        self.logger = logging.getLogger(__name__)
        self.profile_id = -1

        self.loading_window = LoadingWindow()
        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

    def handle_refresh(self):
        self.ui.refreshBtn.setEnabled(False)
        self.search_scrape = SearchScrape()
        self.search_scrape.start()
        self.search_scrape.finished.connect(self.handle_search_scrape_finished)

    def handle_search_scrape_finished(self):
        response = self.search_scrape.get_response()
        self.search_scrape = None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the dropdown elements using appropriate selectors
        table = soup.find('table', id='searchTable')

        # Find the dropdown elements within the table
        dropdown_elements = table.select('select')
        self.logger.debug(dropdown_elements)

        # Extract the data from each dropdown element
        dropdown_data = {}
        for dropdown_element in dropdown_elements:
            options = dropdown_element.find_all('option')
            dropdown_data[dropdown_element['name']] = [option.text for option in options]

        # Process or store the extracted data as needed
        # print(dropdown_data)
        # for dropdown in dropdown_data:
        #     print(dropdown)  # Example: Print the data for each dropdown
        
        self.ui.startYearCombo.addItem("Any")
        self.ui.endYearCombo.addItem("Any")
        self.ui.startYearCombo.addItems([str(year) for year in range(2004, 2017)])
        self.ui.endYearCombo.addItems([str(year) for year in range(2004, 2017)])
        self.logger.info("Search scrape finished. Populated search fields.")
        self.ui.refreshBtn.setEnabled(True)

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
