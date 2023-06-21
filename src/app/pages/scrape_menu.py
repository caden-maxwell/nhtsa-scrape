import logging
import json
from time import sleep

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from bs4 import BeautifulSoup

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.scrape.request_handler import ModelUpdateWorker, SearchRefreshWorker

from .data_view import DataView
from .loading_window import LoadingWindow


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.loading_window = LoadingWindow()
        self.profile_id = -1

        self.populate_search()

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submission)
        self.ui.makeCombo.currentIndexChanged.connect(self.handle_make_change)
        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

    def setup(self, data=None):
        self.profile_id = -1
        make = "All"
        model = "All"
        start_year = "All"
        end_year = "All"
        primary_damage = "All"
        secondary_damage = "All"
        min_dv = 0
        max_dv = 0

        if data:
            self.profile_id, make, model, start_year, end_year, primary_damage, secondary_damage, min_dv, max_dv = data
        if self.profile_id > 0:
            self.ui.mainTitle.setText("Re Scrape Profile")
            self.ui.submitBtn.setText("Re-Scrape")
        
        # Disconnect and reconnect the signal to prevent the connected function from being called while the combobox is being populated
        self.ui.makeCombo.currentIndexChanged.disconnect(self.handle_make_change)
        self.ui.makeCombo.setCurrentText(make)
        self.ui.makeCombo.currentIndexChanged.connect(self.handle_make_change)

        # Populate the rest of the comboboxes
        self.ui.modelCombo.setCurrentText(model)
        self.ui.startYearCombo.setCurrentText(str(start_year))
        self.ui.endYearCombo.setCurrentText(str(end_year))
        self.ui.pDmgCombo.setCurrentText(primary_damage)
        self.ui.sDmgCombo.setCurrentText(secondary_damage)
        self.ui.minDvSpin.setValue(min_dv)
        self.ui.maxDvSpin.setValue(max_dv)

    def populate_search(self):
        self.worker = SearchRefreshWorker()
        self.worker.refreshed.connect(self.parse_refresh)
        self.worker.start()

    def parse_refresh(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', id='searchTable')
        dropdowns = table.select('select')

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all('option')
            dropdown_data[dropdown['name']] = [option.text for option in options]
        
        self.logger.debug(f"Dropdown data:\n{json.dumps(dropdown_data, indent=4)}")

        # Clear the comboboxes
        self.ui.makeCombo.clear()
        self.ui.modelCombo.clear()
        self.ui.startYearCombo.clear()
        self.ui.endYearCombo.clear()
        self.ui.pDmgCombo.clear()
        self.ui.sDmgCombo.clear()

        # Alphabetize model list
        dropdown_data['ddlModel'].sort()
        dropdown_data['ddlModel'].remove("All")
        dropdown_data['ddlModel'].insert(0, "All")

        # Add the dropdown data to the appropriate comboboxes
        self.ui.makeCombo.addItems(dropdown_data['ddlMake'])
        self.ui.modelCombo.addItems(dropdown_data['ddlModel'])
        self.ui.startYearCombo.addItems(dropdown_data['ddlStartModelYear'])
        self.ui.endYearCombo.addItems(dropdown_data['ddlEndModelYear'])
        self.ui.pDmgCombo.addItems(dropdown_data['ddlPrimaryDamage'])
        self.ui.sDmgCombo.addItems(dropdown_data['lSecondaryDamage'])
        
        self.logger.info("Search scrape finished. Populated search fields.")

    def handle_make_change(self, make):
        make = self.ui.makeCombo.itemText(make)
        self.worker = ModelUpdateWorker(make)
        self.worker.updated.connect(self.update_model_combo)
        self.worker.start()

    def update_model_combo(self, response):
        model_dcts = json.loads(response)
        models = []
        for model in model_dcts:
            models.append(model['Value'])
        models.sort()
        self.ui.modelCombo.clear()
        self.ui.modelCombo.addItem("All")
        self.ui.modelCombo.addItems(models)
        self.logger.info("Model update finished. Populated model field.")

    def handle_submission(self):
        self.loading_window.show()

    def open_data_viewer(self):
        self.data_viewer = DataView(self.is_new_profile())
        self.data_viewer.show()

    def is_new_profile(self):
        return self.profile_id < 0
    