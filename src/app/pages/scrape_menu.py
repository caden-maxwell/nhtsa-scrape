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
        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)
        self.ui.imageSetCombo.addItems(["All", "F - Front", "FL - Front Left", "FR - Front Right", "B - Back", "BL - Back Left", "BR - Back Right", "L - Left", "R - Right"])

        self.logger = logging.getLogger(__name__)
        self.scrape_engine = ScrapeEngine()

        # Set up signals to update the scrape engine payload when the user changes any search criteria
        self.ui.makeCombo.currentTextChanged.connect(self.fetch_models)
        self.ui.makeCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('ddlMake', self.ui.makeCombo.currentData()))
        self.ui.modelCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('ddlModel', self.ui.modelCombo.currentData()))
        self.ui.startYearCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('ddlStartModelYear', self.ui.startYearCombo.currentData()))
        self.ui.endYearCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('ddlEndModelYear', self.ui.endYearCombo.currentData()))
        self.ui.pDmgCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('ddlPrimaryDamage', self.ui.pDmgCombo.currentData()))
        self.ui.sDmgCombo.currentTextChanged.connect(lambda: self.scrape_engine.update_payload('lSecondaryDamage', self.ui.sDmgCombo.currentData()))
        self.ui.dvMinSpin.valueChanged.connect(lambda: self.scrape_engine.update_payload('tDeltaVFrom', self.ui.dvMinSpin.value()))
        self.ui.dvMaxSpin.valueChanged.connect(lambda: self.scrape_engine.update_payload('tDeltaVTo', self.ui.dvMaxSpin.value()))
        self.ui.casesSpin.valueChanged.connect(self.limit_cases)
        self.ui.imageSetCombo.currentTextChanged.connect(self.limit_images)
        
        self.loading_window = LoadingWindow(self.scrape_engine)
        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

        self.fetch_search()

    def showEvent(self, event):
        self.fetch_search()
        return super().showEvent(event)

    def fetch_search(self):
        """Fetches the NASS/CDS search website and calls parse_retrieved once there is a response."""
        self.refresh_worker = SearchRefreshWorker()
        self.refresh_worker.retrieved.connect(self.parse_search)
        self.refresh_worker.start()

    def parse_search(self, response):
        """Parses the response from the NASS/CDS search website and populates the search fields."""

        # Parse response
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', id='searchTable')
        dropdowns = table.select('select')

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all('option')
            dropdown_data[dropdown['name']] = [(option.text,option.get('value')) for option in options]
        
        # Block signals temporarily to prevent unnessesary call to handle_make_change while populating make dropdown
        self.ui.makeCombo.blockSignals(True)
        for data in dropdown_data['ddlMake']:
            self.ui.makeCombo.addItem(*data)
        self.ui.makeCombo.blockSignals(False)

        # Populate remaining dropdowns
        for data in dropdown_data['ddlModel']:
            self.ui.modelCombo.addItem(*data)

        for data in dropdown_data['ddlStartModelYear']:
            self.ui.startYearCombo.addItem(*data)
        
        for data in dropdown_data['ddlEndModelYear']:
            self.ui.endYearCombo.addItem(*data)

        for data in dropdown_data['ddlPrimaryDamage']:
            self.ui.pDmgCombo.addItem(*data)
            
        for data in dropdown_data['lSecondaryDamage']:
            self.ui.sDmgCombo.addItem(*data)
        
        self.logger.info("Search fields populated.")

    def fetch_models(self, make):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        self.update_worker = ModelUpdateWorker(make)
        self.update_worker.updated.connect(self.update_model_dropdown)
        self.update_worker.start()

    def update_model_dropdown(self, response):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response)
        models = []
        for model in model_dcts:
            models.append((model['Value'], model['Key']))
        models.sort()

        # Block signals temporarily to prevent unnessesary call to update_model while clearing dropdown
        self.ui.modelCombo.blockSignals(True)
        self.ui.modelCombo.clear()
        self.ui.modelCombo.blockSignals(False)

        # Populate model dropdown
        self.ui.modelCombo.addItem("All", -1)
        for model in models:
            self.ui.modelCombo.addItem(*model)
        self.logger.info("Updated model dropdown.")

    def limit_cases(self, cases):
        self.scrape_engine.case_limit = cases

    def limit_images(self, image_set):
        self.scrape_engine.image_set = image_set

    def handle_submit(self):
        """Starts the scrape engine with the given parameters."""
        self.scrape_engine.start()
        self.loading_window.exec()

    def open_data_viewer(self):
        """Opens the data viewer window, terminating the scrape engine if it is running."""
        if self.scrape_engine.isRunning():
            self.logger.info("Scrape engine is running. Terminating.")
            self.scrape_engine.requestInterruption()
            self.scrape_engine.wait()
        self.data_viewer = DataView(True)
        self.data_viewer.show()
