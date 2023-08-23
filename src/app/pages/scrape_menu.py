import json
import logging
from datetime import datetime

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt6.QtWidgets import QWidget, QMessageBox

from bs4 import BeautifulSoup

from app.models.db_handler import DatabaseHandler
from app.scrape import RequestHandler, ScrapeEngine, RequestQueueItem, Priority
from app.ui.ScrapeMenu_ui import Ui_ScrapeMenu

from . import DataView


class ScrapeMenu(QWidget):
    back = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.profile_id = -1
        self.scrape_engine = None
        self.engine_thread = None
        self.db_handler = db_handler

        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)
        self.ui.noMaxCheckbox.clicked.connect(self.toggle_max_cases)

        self.ui.makeCombo.currentTextChanged.connect(self.fetch_models)
        self.complete_timer = QTimer()

        self.data_viewer = None

    def fetch_search(self):
        """Fetches the NASS/CDS search website and calls parse_retrieved once there is a response."""
        if not self.req_handler.contains(
            priority=Priority.ALL_COMBOS.value
        ):  # We only ever need one of these requests at a time
            request = RequestQueueItem(
                "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search",
                priority=Priority.ALL_COMBOS.value,
            )
            self.req_handler.enqueue_request(request)

    @pyqtSlot(int, str, bytes, str, dict)
    def handle_response(self, priority, url, response_content, cookie, extra_data):
        if priority == Priority.ALL_COMBOS.value:
            self.update_all_dropdowns(response_content)
        elif priority == Priority.MODEL_COMBO.value:
            self.update_model_dropdown(response_content)

    def update_all_dropdowns(self, response_content):
        """Parses the response from the NASS/CDS search website and populates the search fields."""

        # Parse response
        soup = BeautifulSoup(response_content, "html.parser")
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
        request = RequestQueueItem(
            "https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/",
            method="POST",
            params={"make": make},
            priority=Priority.MODEL_COMBO.value,
        )
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value)
        self.req_handler.enqueue_request(request)

    def update_model_dropdown(self, response_content):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response_content)
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

        case_limit = (
            self.ui.casesSpin.value()
            if not self.ui.noMaxCheckbox.isChecked()
            else 100000
        )

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
            "max_cases": case_limit,
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

        self.scrape_engine = ScrapeEngine(
            {
                "ddlMake": self.ui.makeCombo.currentData(),
                "ddlModel": self.ui.modelCombo.currentData(),
                "ddlStartModelYear": self.ui.startYearCombo.currentData(),
                "ddlEndModelYear": self.ui.endYearCombo.currentData(),
                "ddlPrimaryDamage": self.ui.pDmgCombo.currentData(),
                "lSecondaryDamage": self.ui.sDmgCombo.currentData(),
                "tDeltaVFrom": self.ui.dvMinSpin.value(),
                "tDeltaVTo": self.ui.dvMaxSpin.value(),
            },
            case_limit,
        )

        self.scrape_engine.completed.connect(self.handle_scrape_complete)
        self.scrape_engine.event_parsed.connect(self.add_event)

        self.engine_thread = QThread()
        self.scrape_engine.moveToThread(self.engine_thread)
        self.engine_thread.started.connect(self.scrape_engine.start)
        self.engine_thread.start()

        self.complete_timer.timeout.connect(self.scrape_engine.check_complete)
        self.complete_timer.start(500)  # Check if scrape is complete every 0.5s

    @pyqtSlot(dict, bytes, str)
    def add_event(self, event, response_content, cookie):
        self.db_handler.add_event(event, self.profile_id)
        if self.data_viewer:
            self.data_viewer.events_tab.cache_response(
                int(event["case_id"]), response_content, cookie
            )
            self.data_viewer.update_current_tab()

    def handle_scrape_complete(self):
        self.profile_id = -1
        self.complete_timer.stop()

        self.scrape_engine = None
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

    def toggle_max_cases(self, checked):
        self.ui.casesSpin.setEnabled(not checked)

    def cleanup(self):
        self.complete_timer.stop()
        if self.scrape_engine and self.scrape_engine.running:
            self.scrape_engine.complete()
