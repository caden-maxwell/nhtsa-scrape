from dataclasses import dataclass
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Response

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QWidget, QMessageBox, QComboBox, QCheckBox, QSpinBox

from app.models import DatabaseHandler
from app.pages import DataView
from app.scrape import (
    RequestHandler,
    BaseScraper,
    ScraperNASS,
    ScraperCISS,
    RequestQueueItem,
    Priority,
)
from app.ui import Ui_ScrapeMenu


@dataclass
class _SEARCH_MODEL:
    scraper: BaseScraper  # The scraper to use
    html_name: str  # The name of the HTML tag containing the dropdown options
    html_id: str  # The ID of the HTML tag containing the dropdown options
    make: QComboBox  # The make dropdown
    model: QComboBox  # The model dropdown
    models_url: str
    start_model_year: QComboBox  # The start model year dropdown
    end_model_year: QComboBox  # The end model year dropdown
    primary_dmg: QComboBox  # The primary damage dropdown
    secondary_dmg: QComboBox  # The secondary damage dropdown
    min_dv: QSpinBox  # The minimum delta-v spinbox
    max_dv: QSpinBox  # The maximum delta-v spinbox
    enabled_status: QCheckBox  # The checkbox to enable a certain database


class ScrapeMenu(QWidget):
    back = pyqtSignal()
    end_scrape = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.profile_id = -1
        self.scrapers: list[BaseScraper] = []
        self.engine_thread: QThread = None
        self.db_handler = db_handler

        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)

        self.nass_model = _SEARCH_MODEL(
            scraper=ScraperNASS,
            html_name="table",
            html_id="searchTable",
            make=self.ui.makeCombo,
            model=self.ui.modelCombo,
            models_url="https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/",
            start_model_year=self.ui.startYearCombo,
            end_model_year=self.ui.endYearCombo,
            primary_dmg=self.ui.pDmgCombo,
            secondary_dmg=self.ui.sDmgCombo,
            min_dv=self.ui.dvMinSpin,
            max_dv=self.ui.dvMaxSpin,
            enabled_status=self.ui.nassCheckbox,
        )

        self.ciss_model = _SEARCH_MODEL(
            scraper=ScraperCISS,
            html_name="div",
            html_id="panel-options",
            make=self.ui.makeCombo_2,
            model=self.ui.modelCombo_2,
            models_url="https://crashviewer.nhtsa.dot.gov/SCI/GetvPICVehicleModelbyMake/",
            start_model_year=self.ui.startYearCombo_2,
            end_model_year=self.ui.endYearCombo_2,
            primary_dmg=self.ui.pDmgCombo_2,
            secondary_dmg=self.ui.sDmgCombo_2,
            min_dv=self.ui.dvMinSpin_2,
            max_dv=self.ui.dvMaxSpin_2,
            enabled_status=self.ui.cissCheckbox,
        )

        self.ui.makeCombo.activated.connect(lambda: self.fetch_models(self.nass_model))
        self.ui.makeCombo_2.activated.connect(
            lambda: self.fetch_models(self.ciss_model)
        )
        self.ui.nassCheckbox.stateChanged.connect(self.enable_submit)
        self.ui.cissCheckbox.stateChanged.connect(self.enable_submit)

        self.data_viewer = None

    def fetch_search(self):
        """Fetches the NASS and CISS search filter sites to retrieve dropdown options."""
        request_NASS = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search",
            priority=Priority.ALL_COMBOS.value,
            callback=self.update_dropdowns,
            extra_data={"search_model": self.nass_model},
        )
        self.req_handler.enqueue_request(request_NASS)

        request_CISS = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/CISS/SearchFilter",
            priority=Priority.ALL_COMBOS.value,
            callback=self.update_dropdowns,
            extra_data={"search_model": self.ciss_model},
        )
        self.req_handler.enqueue_request(request_CISS)

    @pyqtSlot(RequestQueueItem, Response)
    def handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.ALL_COMBOS.value
            or request.priority == Priority.MODEL_COMBO.value
        ):
            request.callback(request, response)

    def update_dropdowns(self, request: RequestQueueItem, response: Response):
        """Parses the response from a search site and populates the search fields."""
        nhtsa_model: _SEARCH_MODEL = request.extra_data["search_model"]

        # Parse response
        soup = BeautifulSoup(response.content, "html.parser")
        options = soup.find(nhtsa_model.html_name, id=nhtsa_model.html_id)
        dropdowns = options.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        # Populate dropdowns
        nhtsa_model.make.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.make]:
            nhtsa_model.make.addItem(*data)

        self.fetch_models(nhtsa_model)

        nhtsa_model.start_model_year.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.start_model_year]:
            nhtsa_model.start_model_year.addItem(*data)

        nhtsa_model.end_model_year.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.end_model_year]:
            nhtsa_model.end_model_year.addItem(*data)

        nhtsa_model.primary_dmg.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.primary_damage]:
            nhtsa_model.primary_dmg.addItem(*data)

        nhtsa_model.secondary_dmg.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.secondary_damage]:
            nhtsa_model.secondary_dmg.addItem(*data)

        self.logger.info(f"{nhtsa_model.scraper.__name__} search fields populated.")
        nhtsa_model.enabled_status.setEnabled(True)

    def fetch_models(self, search_model: _SEARCH_MODEL):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        extra_data = {"search_model": search_model}
        params = (
            {"make": search_model.make.currentText()}
            if search_model.scraper == ScraperNASS
            else {"makeIds": search_model.make.currentData()}
        )
        request = RequestQueueItem(
            search_model.models_url,
            params=params,
            priority=Priority.MODEL_COMBO.value,
            extra_data=extra_data,
            callback=self.update_model_dropdown,
        )
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value, match_data=extra_data)
        self.req_handler.enqueue_request(request)

    def update_model_dropdown(self, request: RequestQueueItem, response: Response):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response.content)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
        models.sort()

        search_model: _SEARCH_MODEL = request.extra_data["search_model"]

        # Populate model dropdown
        search_model.model.clear()
        search_model.model.addItem("All", -1)
        for model in models:
            search_model.model.addItem(*model)
        self.logger.info(f"Updated {search_model.scraper.__name__} model dropdown.")

    def enable_submit(self):
        """Enables the submit button if at least one database is selected, but not if a scraper is already running."""
        current_scraper = self.__get_current_scraper()
        self.ui.submitBtn.setEnabled(
            (self.ui.nassCheckbox.isChecked() or self.ui.cissCheckbox.isChecked())
            and not (current_scraper and current_scraper.running)
        )

    def handle_submit(self):
        """Starts the scrape engine with the given parameters."""
        self.ui.submitBtn.setEnabled(False)
        self.ui.submitBtn.setText("Scraping...")
        if self.__get_current_scraper():
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
            "max_cases": 999999,
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

        params = {
            "ddlMake": self.ui.makeCombo.currentData(),
            "ddlModel": self.ui.modelCombo.currentData(),
            "ddlStartModelYear": self.ui.startYearCombo.currentData(),
            "ddlEndModelYear": self.ui.endYearCombo.currentData(),
            "ddlPrimaryDamage": self.ui.pDmgCombo.currentData(),
            "lSecondaryDamage": self.ui.sDmgCombo.currentData(),
            "tDeltaVFrom": self.ui.dvMinSpin.value(),
            "tDeltaVTo": self.ui.dvMaxSpin.value(),
        }

        self.scrapers = []
        self.scrapers.append(
            ScraperCISS(params) if self.ui.cissCheckbox.isChecked() else None
        )
        self.scrapers.append(
            ScraperNASS(params) if self.ui.nassCheckbox.isChecked() else None
        )
        self.scrapers = [
            scraper for scraper in self.scrapers if scraper
        ]  # Remove None values
        if not self.scrapers:
            self.logger.error("Scrape aborted: No databases selected.")
            return

        self.engine_thread = QThread()
        prev_scraper: BaseScraper = None
        for scraper in self.scrapers:
            scraper.moveToThread(self.engine_thread)
            if prev_scraper:
                prev_scraper.completed.connect(scraper.start)
            scraper.event_parsed.connect(self.add_event)
            prev_scraper = scraper

        self.scrapers[-1].completed.connect(self.handle_scrape_complete)

        self.engine_thread.started.connect(self.scrapers[0].start)
        self.engine_thread.start()

    def __get_current_scraper(self) -> BaseScraper | None:
        """Returns the running scraper if there is one, otherwise None."""
        for scraper in self.scrapers:
            if scraper.running:
                return scraper
        return None

    @pyqtSlot(dict, Response)
    def add_event(self, event, response):
        if not self.db_handler.get_profile(self.profile_id):
            if self.data_viewer:
                self.data_viewer.close()

            # Remove connection to all next scraper's start signals and complete scrape
            for scraper in self.scrapers:
                scraper.completed.disconnect()

            if current_scraper := self.__get_current_scraper():
                current_scraper.completed.connect(self.handle_scrape_complete)
                self.end_scrape.connect(current_scraper.complete)
                self.end_scrape.emit()
                self.logger.error("Scrape aborted: No profile to add data to.")
            return

        self.db_handler.add_event(event, self.profile_id)
        if self.data_viewer:
            self.data_viewer.events_tab.cache_response(int(event["case_id"]), response)
            self.data_viewer.update_current_tab()

    def handle_scrape_complete(self):
        self.profile_id = -1

        self.scrapers = []
        self.engine_thread.quit()
        self.engine_thread.wait()

        dialog = QMessageBox()
        dialog.setText("Scrape complete.")
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setDefaultButton(QMessageBox.StandardButton.Ok)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle("Scrape Complete")
        dialog.exec()

        self.ui.submitBtn.setEnabled(True)
        self.ui.submitBtn.setText("Scrape")

    def cleanup(self):
        for scraper in self.scrapers:
            scraper.completed.disconnect()

        if current_scraper := self.__get_current_scraper():
            self.logger.warning("Scrape engine is still running. Aborting.")
            current_scraper.completed.connect(self.handle_scrape_complete)
            self.end_scrape.connect(current_scraper.complete)
            self.end_scrape.emit()
