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
        self.loading_window = LoadingWindow()
        self.loading_window.accepted.connect(self.open_data_viewer)
        self.loading_window.rejected.connect(self.end_scrape)

        self.scrape_engine = ScrapeEngine()
        self.scrape_engine.finished.connect(self.loading_window.accept)

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
        self.ui.casesSpin.valueChanged.connect(self.scrape_engine.set_case_limit)
        self.ui.imageSetCombo.currentTextChanged.connect(self.scrape_engine.change_image_set)
        
        self.fetch_search()
        self.ui.casesSpin.setValue(self.scrape_engine.CASES_PER_PAGE)

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
        
        # Block signals temporarily to prevent unnessesary calls to handle_make_change while populating make dropdown
        self.ui.makeCombo.currentTextChanged.disconnect(self.fetch_models)
        self.ui.makeCombo.clear()
        for data in dropdown_data['ddlMake']:
            self.ui.makeCombo.addItem(*data)
        self.ui.makeCombo.currentTextChanged.connect(self.fetch_models)

        # Populate remaining dropdowns
        self.ui.modelCombo.blockSignals(True)
        self.ui.modelCombo.clear()
        self.ui.modelCombo.blockSignals(False)
        for data in dropdown_data['ddlModel']:
            self.ui.modelCombo.addItem(*data)

        self.ui.startYearCombo.blockSignals(True)
        self.ui.startYearCombo.clear()
        self.ui.startYearCombo.blockSignals(False)
        for data in dropdown_data['ddlStartModelYear']:
            self.ui.startYearCombo.addItem(*data)
        
        self.ui.endYearCombo.blockSignals(True)
        self.ui.endYearCombo.clear()
        self.ui.endYearCombo.blockSignals(False)
        for data in dropdown_data['ddlEndModelYear']:
            self.ui.endYearCombo.addItem(*data)

        self.ui.pDmgCombo.blockSignals(True)
        self.ui.pDmgCombo.clear()
        self.ui.pDmgCombo.blockSignals(False)
        for data in dropdown_data['ddlPrimaryDamage']:
            self.ui.pDmgCombo.addItem(*data)
            
        self.ui.sDmgCombo.blockSignals(True)
        self.ui.sDmgCombo.clear()
        self.ui.sDmgCombo.blockSignals(False)
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

        # Populate model dropdown
        self.ui.modelCombo.blockSignals(True)
        self.ui.modelCombo.clear()
        self.ui.modelCombo.blockSignals(False)
        self.ui.modelCombo.addItem("All", -1)
        for model in models:
            self.ui.modelCombo.addItem(*model)
        self.logger.info("Updated model dropdown.")

    def handle_submit(self):
        """Starts the scrape engine with the given parameters."""
        self.ui.submitBtn.setEnabled(False)
        if self.scrape_engine.isRunning():
            self.logger.warning("Scrape engine is already running. Ignoring submission.")
            return
        self.scrape_engine.start()
        self.loading_window.show()

    def open_data_viewer(self):
        """Opens the data viewer window, terminating the scrape engine if it is running."""
        self.end_scrape()
        self.logger.info("Opening data viewer.")
        self.loading_window.close()
        if self.scrape_engine.isRunning():
            self.logger.info("Scrape engine is running. Terminating.")
            self.scrape_engine.requestInterruption()
        self.data_viewer = DataView(True)
        self.data_viewer.show()

    def end_scrape(self):
        """Cancels the scrape engine if it is running."""
        if self.scrape_engine.isRunning():
            self.logger.warning("Scrape engine is running. Requesting interruption...")
            # Block signals temporarily to prevent 'finished' signal from calling open_data_viewer
            self.scrape_engine.blockSignals(True)
            self.scrape_engine.requestInterruption()
            self.scrape_engine.wait()
            self.scrape_engine.blockSignals(False)
            self.logger.info("Scrape stopped.")
        else:
            self.logger.debug("Scrape engine is not running. Ignoring request to end scrape.")
        self.ui.submitBtn.setEnabled(True)
        