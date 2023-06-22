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

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submission)

        self.scrape_engine = ScrapeEngine()
        self.loading_window = LoadingWindow(self.scrape_engine)
        self.loading_window.view_btn_clicked.connect(self.open_data_viewer)

        self.ui.makeCombo.currentTextChanged.connect(self.handle_make_change)
        self.ui.makeCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.makeCombo.currentData()))
        self.ui.modelCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.modelCombo.currentData()))
        self.ui.startYearCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.startYearCombo.currentData()))
        self.ui.endYearCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.endYearCombo.currentData()))
        self.ui.pDmgCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.pDmgCombo.currentData()))
        self.ui.sDmgCombo.currentTextChanged.connect(lambda: self.scrape_engine.set_param(self.ui.sDmgCombo.currentData()))
        self.ui.dvMinSpin.valueChanged.connect(self.scrape_engine.set_param)
        self.ui.dvMaxSpin.valueChanged.connect(self.scrape_engine.set_param)

        self.retrieve_dropdown_data()

    def showEvent(self, event):
        self.refresh_worker.start()
        return super().showEvent(event)

    def retrieve_dropdown_data(self):
        self.refresh_worker = SearchRefreshWorker()
        self.refresh_worker.retrieved.connect(self.parse_retrieved)
        self.refresh_worker.start()

    def parse_retrieved(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find('table', id='searchTable')
        dropdowns = table.select('select')

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all('option')
            dropdown_data[dropdown['name']] = [(option.text,option.get('value')) for option in options]
        
        self.populate_combos(dropdown_data)

    def populate_combos(self, dropdown_data):

        # Disconnect signal temporarily to prevent unnessesary calls to handle_make_change
        self.ui.makeCombo.currentTextChanged.disconnect(self.handle_make_change)
        for data in dropdown_data['ddlMake']:
            self.ui.makeCombo.addItem(*data)
        self.ui.makeCombo.currentTextChanged.connect(self.handle_make_change)

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

    def handle_make_change(self, make):
        self.update_worker = ModelUpdateWorker(make)
        self.update_worker.updated.connect(self.update_model_combo)
        self.update_worker.start()

    def update_model_combo(self, response):
        model_dcts = json.loads(response)
        models = []
        for model in model_dcts:
            models.append((model['Value'], model['Key']))
        models.sort()
        self.ui.modelCombo.disconnect()
        self.ui.modelCombo.clear()
        self.ui.modelCombo.currentTextChanged.connect(lambda s: self.scrape_engine.set_param("model", s))
        self.ui.modelCombo.addItem("All", -1)
        for model in models:
            self.ui.modelCombo.addItem(*model)
        self.logger.info("Updated model dropdown.")

    def handle_submission(self):
        self.scrape_engine.start()
        self.loading_window.exec()

    def open_data_viewer(self):
        if self.scrape_engine.isRunning():
            self.logger.info("Scrape engine is running. Terminating.")
            self.scrape_engine.terminate()
        self.data_viewer = DataView(True)
        self.data_viewer.show()
