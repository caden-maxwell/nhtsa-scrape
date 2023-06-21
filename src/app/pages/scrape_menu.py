import json
import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from bs4 import BeautifulSoup

from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu
from app.scrape import ModelUpdateWorker, SearchRefreshWorker, ScrapeEngine

from .data_view import DataView
from .loading_window import LoadingWindow


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.scrape_engine = ScrapeEngine()
        self.loading_window = LoadingWindow(self.scrape_engine)

        self.get_dropdown_data()

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submission)

        self.ui.makeCombo.currentIndexChanged.connect(self.handle_make_change)
        self.ui.modelCombo.currentIndexChanged.connect(lambda: self.scrape_engine.set_param("model", self.ui.modelCombo.currentText()))
        self.ui.startYearCombo.currentIndexChanged.connect(lambda: self.scrape_engine.set_param("start_year", self.ui.startYearCombo.currentText()))
        self.ui.endYearCombo.currentIndexChanged.connect(lambda: self.scrape_engine.set_param("end_year", self.ui.endYearCombo.currentText()))
        self.ui.pDmgCombo.currentIndexChanged.connect(lambda: self.scrape_engine.set_param("primary_dmg", self.ui.pDmgCombo.currentText()))
        self.ui.sDmgCombo.currentIndexChanged.connect(lambda: self.scrape_engine.set_param("secondary_dmg", self.ui.sDmgCombo.currentText()))
        self.ui.minDvSpin.valueChanged.connect(lambda: self.scrape_engine.set_param("dv_min", self.ui.minDvSpin.value()))
        self.ui.maxDvSpin.valueChanged.connect(lambda: self.scrape_engine.set_param("dv_max", self.ui.maxDvSpin.value()))

        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

    def setup(self):
        self.ui.makeCombo.setCurrentText("All")
        self.ui.modelCombo.setCurrentText("All")
        self.ui.startYearCombo.setCurrentText("All")
        self.ui.endYearCombo.setCurrentText("All")
        self.ui.pDmgCombo.setCurrentText("All")
        self.ui.sDmgCombo.setCurrentText("All")
        self.ui.minDvSpin.setValue(0)
        self.ui.maxDvSpin.setValue(0)

    def get_dropdown_data(self):
        self.worker = SearchRefreshWorker()
        self.worker.retrieved.connect(self.parse_retrieved)
        self.worker.start()

    def parse_retrieved(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', id='searchTable')
        dropdowns = table.select('select')

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all('option')
            dropdown_data[dropdown['name']] = [option.text for option in options]
        
        self.logger.debug(f"Dropdown data:\n{json.dumps(dropdown_data, indent=4)}")

        self.populate_combos(dropdown_data)

    def populate_combos(self, dropdown_data):

        self.ui.makeCombo.addItems(dropdown_data['ddlMake'])
        self.ui.modelCombo.addItems(dropdown_data['ddlModel'])
        self.ui.startYearCombo.addItems(dropdown_data['ddlStartModelYear'])
        self.ui.endYearCombo.addItems(dropdown_data['ddlEndModelYear'])
        self.ui.pDmgCombo.addItems(dropdown_data['ddlPrimaryDamage'])
        self.ui.sDmgCombo.addItems(dropdown_data['lSecondaryDamage'])
        
        self.logger.info("Search fields populated.")

    def handle_make_change(self, make):
        self.scrape_engine.set_param("make", self.ui.makeCombo.itemText(make))
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
        self.scrape_engine.start()
        self.loading_window.exec()

    def open_data_viewer(self):
        if self.scrape_engine.isRunning():
            self.logger.info("Scrape engine is running. Terminating.")
            self.scrape_engine.terminate()
        self.data_viewer = DataView(True)
        self.data_viewer.show()
