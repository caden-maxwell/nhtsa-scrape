from dataclasses import dataclass
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Response

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QWidget, QMessageBox, QComboBox, QRadioButton, QSpinBox

from app.models import DatabaseHandler, Profile, Event
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
class _SearchModel:
    scraper: BaseScraper  # The scraper to use
    html_options_name: str  # The name of the HTML tag containing the dropdown options
    html_options_id: str  # The ID of the HTML tag containing the dropdown options
    make_combo: QComboBox  # The make dropdown
    model_combo: QComboBox  # The model dropdown
    start_year_combo: QComboBox  # The start model year dropdown
    end_year_combo: QComboBox  # The end model year dropdown
    p_dmg_combo: QComboBox  # The primary damage dropdown
    s_dmg_combo: QComboBox  # The secondary damage dropdown
    min_dv_spinbox: QSpinBox  # The minimum delta-v spinbox
    max_dv_spinbox: QSpinBox  # The maximum delta-v spinbox
    radio_button: QRadioButton  # The radio button to enable the scraper


class ScrapeMenu(QWidget):
    back = pyqtSignal()
    end_scrape = pyqtSignal()

    def __init__(self, db_handler: DatabaseHandler):
        super().__init__()

        self.ui = Ui_ScrapeMenu()
        self.ui.setupUi(self)

        self.logger = logging.getLogger(__name__)

        self.profile: Profile = None
        self.scraper: BaseScraper = None
        self.engine_thread: QThread = None
        self.db_handler = db_handler

        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)

        self.ui.backBtn.clicked.connect(self.back.emit)
        self.ui.submitBtn.clicked.connect(self.handle_submit)
        self.ui.stopBtn.clicked.connect(self.end_scrape.emit)
        self.ui.stopBtn.setVisible(False)

        nass_model = _SearchModel(
            scraper=ScraperNASS,
            html_options_name="table",
            html_options_id="searchTable",
            make_combo=self.ui.makeCombo,
            model_combo=self.ui.modelCombo,
            start_year_combo=self.ui.startYearCombo,
            end_year_combo=self.ui.endYearCombo,
            p_dmg_combo=self.ui.pDmgCombo,
            s_dmg_combo=self.ui.sDmgCombo,
            min_dv_spinbox=self.ui.dvMinSpin,
            max_dv_spinbox=self.ui.dvMaxSpin,
            radio_button=self.ui.nassRadioBtn,
        )

        ciss_model = _SearchModel(
            scraper=ScraperCISS,
            html_options_name="div",
            html_options_id="panel-options",
            make_combo=self.ui.makeCombo_2,
            model_combo=self.ui.modelCombo_2,
            start_year_combo=self.ui.startYearCombo_2,
            end_year_combo=self.ui.endYearCombo_2,
            p_dmg_combo=self.ui.pDmgCombo_2,
            s_dmg_combo=self.ui.sDmgCombo_2,
            min_dv_spinbox=self.ui.dvMinSpin_2,
            max_dv_spinbox=self.ui.dvMaxSpin_2,
            radio_button=self.ui.cissRadioBtn,
        )

        self.nhtsa_models = [ciss_model, nass_model]

        self.ui.makeCombo.activated.connect(lambda: self.fetch_models(nass_model))
        self.ui.makeCombo_2.activated.connect(lambda: self.fetch_models(ciss_model))

        self.ui.databaseBtnGroup.buttonClicked.connect(self.enable_submit)

        self.data_viewer = None

    def fetch_search(self):
        """Fetches the NASS and CISS search filter sites to retrieve dropdown options."""
        for nhtsa_model in self.nhtsa_models:
            self.req_handler.enqueue_request(
                RequestQueueItem(
                    BaseScraper.ROOT + nhtsa_model.scraper.search_url,
                    priority=Priority.ALL_COMBOS.value,
                    callback=self.update_dropdowns,
                    extra_data={"search_model": nhtsa_model},
                )
            )

    @pyqtSlot(RequestQueueItem, Response)
    def handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.ALL_COMBOS.value
            or request.priority == Priority.MODEL_COMBO.value
        ):
            request.callback(request, response)

    def update_dropdowns(self, request: RequestQueueItem, response: Response):
        """Parses the response from a search site and populates the search fields."""
        nhtsa_model: _SearchModel = request.extra_data["search_model"]

        # Parse response
        soup = BeautifulSoup(response.content, "html.parser")
        options = soup.find(
            nhtsa_model.html_options_name, id=nhtsa_model.html_options_id
        )
        dropdowns: list[BeautifulSoup] = options.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            options: list[BeautifulSoup]
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        # Populate dropdowns
        nhtsa_model.make_combo.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.make]:
            nhtsa_model.make_combo.addItem(*data)

        self.fetch_models(nhtsa_model)

        nhtsa_model.start_year_combo.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.start_model_year]:
            nhtsa_model.start_year_combo.addItem(*data)

        nhtsa_model.end_year_combo.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.end_model_year]:
            nhtsa_model.end_year_combo.addItem(*data)

        nhtsa_model.p_dmg_combo.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.primary_damage]:
            nhtsa_model.p_dmg_combo.addItem(*data)

        nhtsa_model.s_dmg_combo.clear()
        for data in dropdown_data[nhtsa_model.scraper.field_names.secondary_damage]:
            nhtsa_model.s_dmg_combo.addItem(*data)

        self.logger.info(f"{nhtsa_model.scraper.__name__} search fields populated.")
        nhtsa_model.radio_button.setEnabled(True)

    def fetch_models(self, search_model: _SearchModel):
        """Fetches the models for the given make and calls update_model_dropdown once there is a response."""
        extra_data = {"search_model": search_model}
        self.req_handler.clear_queue(Priority.MODEL_COMBO.value, match_data=extra_data)

        params = (
            {"make": search_model.make_combo.currentText()}
            if search_model.scraper == ScraperNASS
            else {"makeIds": search_model.make_combo.currentData()}
        )
        self.req_handler.enqueue_request(
            RequestQueueItem(
                BaseScraper.ROOT + search_model.scraper.models_url,
                params=params,
                priority=Priority.MODEL_COMBO.value,
                extra_data=extra_data,
                callback=self.update_model_dropdown,
            )
        )

    def update_model_dropdown(self, request: RequestQueueItem, response: Response):
        """Populates the model dropdown with models from the response."""

        # Parse response
        model_dcts = json.loads(response.content)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
        models.sort()

        search_model: _SearchModel = request.extra_data["search_model"]

        # Populate model dropdown
        search_model.model_combo.clear()
        search_model.model_combo.addItem("All", -1)
        for model in models:
            search_model.model_combo.addItem(*model)
        self.logger.info(f"Updated {search_model.scraper.__name__} model dropdown.")

    def enable_submit(self):
        """Enables the submit button if at least one database is selected, but not if a scraper is already running."""
        self.ui.submitBtn.setEnabled(
            any(button.isChecked() for button in self.ui.databaseBtnGroup.buttons())
            and not (self.scraper and self.scraper.running)
        )

    def handle_submit(self):
        """Starts the scrape engine with the given parameters."""
        self.ui.submitBtn.setEnabled(False)
        self.ui.submitBtn.setText("Scraping...")
        self.ui.stopBtn.setVisible(True)

        if self.scraper and self.scraper.running:
            self.logger.warning(
                "Scrape engine is already running. Ignoring submission."
            )
            return

        # Get the active database based on the radio button
        nhtsa_model = next(
            (model for model in self.nhtsa_models if model.radio_button.isChecked()),
            None,
        )

        make = nhtsa_model.make_combo.currentText().upper()
        make_txt = make if make != "ALL" else "ANY MAKE"

        model = nhtsa_model.model_combo.currentText().upper()
        model_txt = model if model != "ALL" else "ANY MODEL"

        start_year = nhtsa_model.start_year_combo.currentText().upper()
        end_year = nhtsa_model.end_year_combo.currentText().upper()

        p_dmg = nhtsa_model.p_dmg_combo.currentText().upper()
        p_dmg_txt = p_dmg if p_dmg != "ALL" else ""

        name = f"{make_txt} {model_txt} ({start_year}-{end_year}) {p_dmg_txt}"
        name = name.replace("(ALL-ALL)", "(ANY YEAR)")
        name = name.replace("(ALL-", "(UP TO ").replace("-ALL)", " OR NEWER)")

        now = datetime.now()
        self.profile = Profile(
            name=name,
            make=make,
            model=model,
            start_year=start_year,
            end_year=end_year,
            primary_dmg=p_dmg,
            secondary_dmg=nhtsa_model.s_dmg_combo.currentText().upper(),
            min_dv=nhtsa_model.min_dv_spinbox.value(),
            max_dv=nhtsa_model.min_dv_spinbox.value(),
            created=int(now.timestamp()),
            modified=int(now.timestamp()),
        )

        self.db_handler.add_profile(self.profile)
        if self.profile.id < 0:
            self.logger.error(
                f"Scrape aborted: No profile to add data to. profile.id={self.profile.id}"
            )
            return

        self.logger.info(f"Created new profile with ID {self.profile.id}.")
        self.data_viewer = DataView(self.db_handler, self.profile, new_profile=True)
        self.data_viewer.show()

        if not nhtsa_model:
            self.logger.error("Scrape aborted: No database selected.")
            return

        self.scraper = nhtsa_model.scraper(
            make=(
                nhtsa_model.make_combo.currentText(),
                int(nhtsa_model.make_combo.currentData()),
            ),
            model=(
                nhtsa_model.model_combo.currentText(),
                int(nhtsa_model.model_combo.currentData()),
            ),
            start_model_year=(
                nhtsa_model.start_year_combo.currentText(),
                int(nhtsa_model.start_year_combo.currentData()),
            ),
            end_model_year=(
                nhtsa_model.end_year_combo.currentText(),
                int(nhtsa_model.end_year_combo.currentData()),
            ),
            primary_damage=(
                nhtsa_model.p_dmg_combo.currentText(),
                int(nhtsa_model.p_dmg_combo.currentData() or -1),
            ),
            secondary_damage=(
                nhtsa_model.s_dmg_combo.currentText(),
                int(nhtsa_model.s_dmg_combo.currentData() or -1),
            ),
            min_dv=nhtsa_model.min_dv_spinbox.value(),
            max_dv=nhtsa_model.max_dv_spinbox.value(),
        )

        # Set up and connect scrapers
        self.engine_thread = QThread()
        self.scraper.moveToThread(self.engine_thread)
        self.scraper.event_parsed.connect(self.add_event)
        self.end_scrape.connect(self.scraper.complete)
        self.scraper.completed.connect(self.handle_scrape_complete)

        self.engine_thread.started.connect(self.scraper.start)
        self.engine_thread.start()

    @pyqtSlot(Event, Response)
    def add_event(self, event: Event, response: Response):
        if not self.profile:
            if self.data_viewer:
                self.data_viewer.close()

            if self.scraper and self.scraper.running:
                self.end_scrape.emit()
                self.logger.error("Scrape aborted: No profile to add data to.")
            return

        self.db_handler.add_event(event, self.profile)
        if self.data_viewer:
            self.data_viewer.events_tab.cache_response(event.case_id, response)
            self.data_viewer.update_current_tab()

    def handle_scrape_complete(self):
        self.profile = None

        self.scraper = None
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
        self.ui.stopBtn.setVisible(False)

    def cleanup(self):
        if self.scraper and self.scraper.running:
            self.logger.warning("Scrape engine is still running. Aborting.")
            self.end_scrape.emit()
