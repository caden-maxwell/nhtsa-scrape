import json
import logging
import time

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt6.QtWidgets import QWidget

from bs4 import BeautifulSoup

from app.models.scrape_profiles import ScrapeProfiles
from app.scrape import RequestHandler, ScrapeEngine, Request, Priority
from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu

from .data_view import DataView


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)
        self.scrape_engine = None
        self.engine_thread = None

        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)
        self.ui.imageSetCombo.addItems(
            [
                "All",
                "F - Front",
                "FL - Front Left",
                "FR - Front Right",
                "B - Back",
                "BL - Back Left",
                "BR - Back Right",
                "L - Left",
                "R - Right",
            ]
        )

        self.ui.makeCombo.currentTextChanged.connect(self.fetch_models)
        self.ui.casesSpin.setValue(40)
        self.engine_timer = QTimer()

        self.data_viewer = None

    def fetch_search(self):
        """Fetches the NASS/CDS search website and calls parse_retrieved once there is a response."""
        if not self.req_handler.contains(
            priority=Priority.ALL_COMBOS.value
        ):  # We only ever need one of these requests at a time
            request = Request(
                "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search",
                priority=Priority.ALL_COMBOS.value,
            )
            self.req_handler.enqueue_request(request)

    @pyqtSlot(int, str, str, str)
    def handle_response(self, priority, url, response_text, cookie):
        if priority == Priority.ALL_COMBOS.value:
            self.update_all_dropdowns(response_text)
        elif priority == Priority.MODEL_COMBO.value:
            self.update_model_dropdown(response_text)

    def update_all_dropdowns(self, response):
        """Parses the response from the NASS/CDS search website and populates the search fields."""

        # Parse response
        soup = BeautifulSoup(response, "html.parser")
        table = soup.find("table", id="searchTable")
        dropdowns = table.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        # Block signals temporarily to prevent unnessesary calls to handle_make_change while populating make dropdown
        self.ui.makeCombo.currentTextChanged.disconnect(self.fetch_models)
        self.ui.makeCombo.clear()
        for data in dropdown_data["ddlMake"]:
            self.ui.makeCombo.addItem(*data)
        self.ui.makeCombo.currentTextChanged.connect(self.fetch_models)

        # Populate remaining dropdowns
        self.ui.modelCombo.blockSignals(True)
        self.ui.modelCombo.clear()
        self.ui.modelCombo.blockSignals(False)
        for data in dropdown_data["ddlModel"]:
            self.ui.modelCombo.addItem(*data)

        self.ui.startYearCombo.blockSignals(True)
        self.ui.startYearCombo.clear()
        self.ui.startYearCombo.blockSignals(False)
        for data in dropdown_data["ddlStartModelYear"]:
            self.ui.startYearCombo.addItem(*data)

        self.ui.endYearCombo.blockSignals(True)
        self.ui.endYearCombo.clear()
        self.ui.endYearCombo.blockSignals(False)
        for data in dropdown_data["ddlEndModelYear"]:
            self.ui.endYearCombo.addItem(*data)

        self.ui.pDmgCombo.blockSignals(True)
        self.ui.pDmgCombo.clear()
        self.ui.pDmgCombo.blockSignals(False)
        for data in dropdown_data["ddlPrimaryDamage"]:
            self.ui.pDmgCombo.addItem(*data)

        self.ui.sDmgCombo.blockSignals(True)
        self.ui.sDmgCombo.clear()
        self.ui.sDmgCombo.blockSignals(False)
        for data in dropdown_data["lSecondaryDamage"]:
            self.ui.sDmgCombo.addItem(*data)

        self.ui.submitBtn.setEnabled(True)
        self.logger.info("Search fields populated.")

    def fetch_models(self, make):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        request = Request(
            "https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/",
            method="POST",
            params={"make": make},
            priority=Priority.MODEL_COMBO.value,
        )
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value)
        self.req_handler.enqueue_request(request)

    def update_model_dropdown(self, response):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
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
        self.ui.submitBtn.setText("Scraping...")
        if self.scrape_engine and self.scrape_engine.running:
            self.logger.warning(
                "Scrape engine is already running. Ignoring submission."
            )
            return

        search_params = {
            "ddlMake": self.ui.makeCombo.currentData(),
            "ddlModel": self.ui.modelCombo.currentData(),
            "ddlStartModelYear": self.ui.startYearCombo.currentData(),
            "ddlEndModelYear": self.ui.endYearCombo.currentData(),
            "ddlPrimaryDamage": self.ui.pDmgCombo.currentData(),
            "lSecondaryDamage": self.ui.sDmgCombo.currentData(),
            "tDeltaVFrom": self.ui.dvMinSpin.value(),
            "tDeltaVTo": self.ui.dvMaxSpin.value(),
        }
        image_set = self.ui.imageSetCombo.currentText()
        case_limit = self.ui.casesSpin.value()

        self.scrape_engine = ScrapeEngine(search_params, image_set, case_limit)
        self.scrape_engine.completed.connect(self.handle_scrape_complete)

        profile_model = ScrapeProfiles()

        make = self.ui.makeCombo.currentText().upper()
        model = self.ui.modelCombo.currentText().upper()
        start_year = self.ui.startYearCombo.currentText().upper()
        end_year = self.ui.endYearCombo.currentText().upper()
        p_dmg = self.ui.pDmgCombo.currentText().upper()
        dv_min = self.ui.dvMinSpin.value() if self.ui.dvMinSpin.value() else "0"
        dv_max = self.ui.dvMaxSpin.value() if self.ui.dvMaxSpin.value() else "INF"

        name = f"{make}_{model}_{start_year},{end_year}_{p_dmg}_dv{dv_min},{dv_max}"
        name = name.replace(" ", "")
        new_profile = {
            "name": name,
            "description": "",
            "created": time.time(),
            "modified": time.time(),
        }

        profile_id = profile_model.add_data(new_profile)
        self.data_viewer = DataView(profile_id)
        self.data_viewer.show()

        self.scrape_engine.event_parsed.connect(self.data_viewer.add_event)

        self.engine_thread = QThread()
        self.scrape_engine.moveToThread(self.engine_thread)
        self.engine_thread.started.connect(self.scrape_engine.start)
        self.engine_thread.start()

        self.engine_timer.timeout.connect(self.scrape_engine.check_complete)
        self.engine_timer.start(1000)

    def handle_scrape_complete(self):
        self.engine_thread.quit()
        self.engine_thread.wait()

        self.data_viewer.scrape_complete()

        self.ui.submitBtn.setEnabled(True)
        self.ui.submitBtn.setText("Scrape")

    def cleanup(self):
        self.engine_timer.stop()
        if self.scrape_engine and self.scrape_engine.running:
            self.scrape_engine.stop()
        if self.engine_thread and self.engine_thread.isRunning():
            self.engine_thread.quit()
            self.engine_thread.wait()
