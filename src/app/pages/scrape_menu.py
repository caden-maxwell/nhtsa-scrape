import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Response

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt6.QtWidgets import QWidget, QMessageBox

from app.models import DatabaseHandler
from app.pages import DataView
from app.scrape import RequestHandler, ScraperNASS, RequestQueueItem, Priority
from app.ui import Ui_ScrapeMenu


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.profile_id = -1
        self.scraper = None
        self.engine_thread = None
        self.db_handler = db_handler

        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)

        self.ui.makeCombo.activated.connect(self.fetch_models_nass)
        self.ui.makeCombo_2.activated.connect(self.fetch_models_ciss)
        self.ui.nassCheckbox.stateChanged.connect(self.enable_submit)
        self.ui.cissCheckbox.stateChanged.connect(self.enable_submit)

        self.data_viewer = None
        self.complete_timer = QTimer()

    def fetch_search(self):
        """Fetches the NASS and CISS search filter sites to retrieve dropdown options."""
        request_NASS = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search",
            priority=Priority.ALL_COMBOS.value,
            extra_data={"database": "NASS"},
            callback=self.update_nass_dropdowns,
        )
        self.req_handler.enqueue_request(request_NASS)

        request_CISS = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/CISS/SearchFilter",
            priority=Priority.ALL_COMBOS.value,
            extra_data={"database": "CISS"},
            callback=self.update_ciss_dropdowns,
        )
        self.req_handler.enqueue_request(request_CISS)

    @pyqtSlot(RequestQueueItem, Response)
    def handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.ALL_COMBOS.value
            or request.priority == Priority.MODEL_COMBO.value
        ):
            request.callback(request, response)

    def update_nass_dropdowns(self, request: RequestQueueItem, response: Response):
        """Parses the response from the NASS search site and populates the search fields."""

        # Parse response
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", id="searchTable")
        dropdowns = table.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        # Populate dropdowns
        self.ui.makeCombo.clear()
        for data in dropdown_data["ddlMake"]:
            self.ui.makeCombo.addItem(*data)

        self.ui.startYearCombo.clear()
        for data in dropdown_data["ddlStartModelYear"]:
            self.ui.startYearCombo.addItem(*data)

        self.ui.endYearCombo.clear()
        for data in dropdown_data["ddlEndModelYear"]:
            self.ui.endYearCombo.addItem(*data)

        self.ui.pDmgCombo.clear()
        for data in dropdown_data["ddlPrimaryDamage"]:
            self.ui.pDmgCombo.addItem(*data)

        self.ui.sDmgCombo.clear()
        for data in dropdown_data["lSecondaryDamage"]:
            self.ui.sDmgCombo.addItem(*data)

        self.logger.info("NASS search fields populated.")
        self.ui.nassCheckbox.setEnabled(True)

    def update_ciss_dropdowns(self, request: RequestQueueItem, response: Response):
        soup = BeautifulSoup(response.content, "html.parser")
        options = soup.find("div", id="panel-options")
        dropdowns = options.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        self.ui.makeCombo_2.clear()
        self.ui.startYearCombo_2.addItem("All", -1)
        for data in dropdown_data["vPICVehicleMakes"]:
            self.ui.makeCombo_2.addItem(*data)

        self.ui.startYearCombo_2.clear()
        self.ui.startYearCombo_2.addItem("All", -1)
        for data in dropdown_data["VehicleModelYears"]:
            self.ui.startYearCombo_2.addItem(*data)

        self.ui.endYearCombo_2.clear()
        self.ui.endYearCombo_2.addItem("All", -1)
        for data in dropdown_data["VehicleModelYears"]:
            self.ui.endYearCombo_2.addItem(*data)

        self.ui.pDmgCombo_2.clear()
        for data in dropdown_data["VehicleDamageImpactPlane"]:
            self.ui.pDmgCombo_2.addItem(*data)

        self.ui.sDmgCombo_2.clear()
        for data in dropdown_data["VehicleDamageImpactSubSection"]:
            self.ui.sDmgCombo_2.addItem(*data)

        self.logger.info("CISS search fields populated.")
        self.ui.cissCheckbox.setEnabled(True)

    def enable_submit(self):
        """Enables the submit button if at least one database is selected."""
        self.ui.submitBtn.setEnabled(self.ui.nassCheckbox.isChecked() or self.ui.cissCheckbox.isChecked())

    def fetch_models_nass(self, idx):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        extra_data = {"database": "NASS"}
        request = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/",
            params={"make": self.ui.makeCombo.currentText()},
            priority=Priority.MODEL_COMBO.value,
            extra_data=extra_data,
            callback=self.update_model_dropdown_nass,
        )
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value, match_data=extra_data)
        self.req_handler.enqueue_request(request)

    def fetch_models_ciss(self, idx):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        extra_data = {"database": "CISS"}
        request = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/SCI/GetvPICVehicleModelbyMake/",
            params={"MakeIds": self.ui.makeCombo_2.currentData()},
            priority=Priority.MODEL_COMBO.value,
            extra_data=extra_data,
            callback=self.update_model_dropdown_ciss,
        )
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value, match_data=extra_data)
        self.req_handler.enqueue_request(request)

    def update_model_dropdown_nass(self, request: RequestQueueItem, response: Response):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response.content)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
        models.sort()

        # Populate model dropdown
        self.ui.modelCombo.clear()
        self.ui.modelCombo.addItem("All", -1)
        for model in models:
            self.ui.modelCombo.addItem(*model)
        self.logger.info("Updated NASS model dropdown.")

    def update_model_dropdown_ciss(self, request: RequestQueueItem, response: Response):
        """Populates the CISS model dropdown vehicle models from the response."""

        # Parse response
        model_dcts = json.loads(response.content)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
        models.sort()

        # Populate model dropdown
        self.ui.modelCombo_2.clear()
        self.ui.modelCombo_2.addItem("All", -1)
        for model in models:
            self.ui.modelCombo_2.addItem(*model)
        self.logger.info("Updated CISS model dropdown.")

    def handle_submit(self):
        """Starts the scrape engine with the given parameters."""
        self.ui.submitBtn.setEnabled(False)
        self.ui.submitBtn.setText("Scraping...")
        if self.scraper and self.scraper.running:
            self.logger.warning(
                "Scrape engine is already running. Ignoring submission."
            )
            return

        make = self.ui.makeCombo.currentText().upper()
        make_txt = make if make != "ALL" else "ANY MAKE"

        model = self.ui.modelCombo.currentText().upper()
        model_txt = model if model != "ALL" else "ANY MODEL"

        start_year = self.ui.startYearCombo.currentText().upper()
        end_year = self.ui.endYearCombo.currentText().upper()

        p_dmg = self.ui.pDmgCombo.currentText().upper()
        p_dmg_txt = p_dmg if p_dmg != "ALL" else ""

        name = f"{make_txt} {model_txt} ({start_year}-{end_year}) {p_dmg_txt}"
        name = name.replace("(ALL-ALL)", "(ANY YEAR)")
        name = name.replace("(ALL-", "(UP TO ").replace("-ALL)", " OR NEWER)")

        now = datetime.now()
        new_profile = {
            "name": name,
            "description": "None",
            "make": make,
            "model": model,
            "start_year": start_year,
            "end_year": end_year,
            "primary_dmg": p_dmg,
            "secondary_dmg": self.ui.sDmgCombo.currentText().upper(),
            "min_dv": self.ui.dvMinSpin.value(),
            "max_dv": self.ui.dvMaxSpin.value(),
            "max_cases": 100000,
            "created": int(now.timestamp()),
            "modified": int(now.timestamp()),
        }

        self.profile_id = self.db_handler.add_profile(new_profile)
        if self.profile_id < 0:
            self.logger.error("Scrape aborted: No profile to add data to.")
            return

        self.logger.info(f"Created new profile with ID {self.profile_id}.")
        self.data_viewer = DataView(self.db_handler, self.profile_id, new_profile=True)
        self.data_viewer.show()

        self.scraper = ScraperNASS(
            {
                "ddlMake": self.ui.makeCombo.currentData(),
                "ddlModel": self.ui.modelCombo.currentData(),
                "ddlStartModelYear": self.ui.startYearCombo.currentData(),
                "ddlEndModelYear": self.ui.endYearCombo.currentData(),
                "ddlPrimaryDamage": self.ui.pDmgCombo.currentData(),
                "lSecondaryDamage": self.ui.sDmgCombo.currentData(),
                "tDeltaVFrom": self.ui.dvMinSpin.value(),
                "tDeltaVTo": self.ui.dvMaxSpin.value(),
            }
        )

        self.scraper.completed.connect(self.handle_scrape_complete)
        self.scraper.event_parsed.connect(self.add_event)

        self.engine_thread = QThread()
        self.scraper.moveToThread(self.engine_thread)
        self.engine_thread.started.connect(self.scraper.start)
        self.engine_thread.start()

        self.complete_timer.timeout.connect(self.scraper.check_complete)
        self.complete_timer.start(500)  # Check if scrape is complete every 0.5s

    @pyqtSlot(dict, Response)
    def add_event(self, event, response):
        if not self.db_handler.get_profile(self.profile_id):
            if self.data_viewer:
                self.data_viewer.close()
            if self.scraper:
                self.scraper.complete()
                self.logger.error("Scrape aborted: No profile to add data to.")
            return
        self.db_handler.add_event(event, self.profile_id)
        if self.data_viewer:
            self.data_viewer.events_tab.cache_response(int(event["case_id"]), response)
            self.data_viewer.update_current_tab()

    def handle_scrape_complete(self):
        self.profile_id = -1
        self.complete_timer.stop()

        self.scraper = None
        self.engine_thread.quit()
        self.engine_thread.wait()

        dialog = QMessageBox()
        dialog.setText("Scrape complete. :)")
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setDefaultButton(QMessageBox.StandardButton.Ok)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle("Scrape Complete")
        dialog.exec()

        self.ui.submitBtn.setEnabled(True)
        self.ui.submitBtn.setText("Scrape")

    def toggle_max_cases(self, checked):
        self.ui.casesSpin.setEnabled(not checked)

    def cleanup(self):
        self.complete_timer.stop()
        if self.scraper and self.scraper.running:
            self.scraper.complete()
