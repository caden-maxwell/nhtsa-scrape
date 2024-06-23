from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import logging
import textwrap
from typing import Generic, TypeVar
from requests import Response

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

from app.scrape import RequestHandler, RequestQueueItem, Priority
from app.models import Event

T = TypeVar("T", str, int)


@dataclass
class ScrapeParams(Generic[T]):
    """Dataclass for dropdown field names (str) or values (int) for each parameter of the scraper."""

    make: T
    model: T
    start_model_year: T
    end_model_year: T
    primary_damage: T
    secondary_damage: T
    min_dv: T
    max_dv: T


class _Meta(type(ABC), type(QObject)):
    """Metaclass for BaseScraper."""


class BaseScraper(QObject, ABC, metaclass=_Meta):
    event_parsed = pyqtSignal(Event, Response)
    started = pyqtSignal()
    completed = pyqtSignal()
    ROOT = "https://crashviewer.nhtsa.dot.gov/"

    @property
    @abstractmethod
    def search_url(self) -> str:
        """The URL for the search filters (dropdowns) page."""

    @property
    @abstractmethod
    def models_url(self) -> str:
        """The URL for vehicle models."""

    @property
    @abstractmethod
    def case_url(self, case_id) -> str:
        """The URL for a specific case."""

    @property
    @abstractmethod
    def case_url_raw(self, case_id) -> str:
        """The URL for a specific case which returns data in parseable format."""

    @property
    @abstractmethod
    def case_list_url(self) -> str:
        """The URL for a list of cases."""

    @property
    @abstractmethod
    def img_url(self) -> str:
        """The URL for an image."""

    @property
    @abstractmethod
    def field_names(self) -> ScrapeParams[str]:
        """Returns a dataclass of dropdown field names for each parameter of the scraper."""

    @abstractmethod
    def __init__(self):
        """
        Initializes the BaseScraper. Do not make any signal/slot connections here,
        as this function will be run in the main thread. If you need to connect signals/slots,
        do so in the start() function.
        """
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._req_handler = RequestHandler()

        self.running = False
        self.start_time = datetime.now()

        self.current_page = 1
        self.success_cases = 0
        self.failed_cases = 0
        self.total_events = 0

        self._payload = {}

    def start(self):
        self._req_handler.response_received.connect(
            self._handle_response
        )  # This needs to be connected here instead of init to avoid running in the main thread

        self._timer = QTimer()
        self._timer.setInterval(500)  # Every 0.5 seconds
        self._timer.timeout.connect(self._check_complete)
        self._timer.start()

        self.running = True
        self.started.emit()

        self._scrape()

    @abstractmethod
    def _convert_params_to_payload(self, params: ScrapeParams[int]) -> dict:
        """Converts the user's search parameters to the payload format of the scraper."""

    @abstractmethod
    def _scrape(self):
        """Starts the scraping process."""

    @pyqtSlot(RequestQueueItem, Response)
    @abstractmethod
    def _handle_response(self, request: RequestQueueItem, response: Response):
        """Handles the response from a request."""

    def _check_complete(self):
        """Checks if the scraper can be completed and emits the completed signal if so."""
        if (
            not (
                self._req_handler.contains(Priority.CASE_LIST.value)
                or self._req_handler.contains(Priority.CASE.value)
            )
            and self.running
        ):
            self.complete()

    def complete(self):
        """Completes the scraping process and emits the completed signal."""

        # Order matters here, otherwise the request handler will start making
        # unnecessary case list requests once the individual cases are cleared
        self._req_handler.clear_queue(Priority.CASE_LIST.value)
        self._req_handler.clear_queue(Priority.CASE.value)

        if self.success_cases + self.failed_cases < 1:
            self._logger.info("No data was found. Scrape complete.")
        else:
            total_cases = self.success_cases + self.failed_cases
            self._logger.info(
                textwrap.dedent(
                    f"""
                ---- Scrape Summary ----
                - Total Cases Requested: {total_cases}
                    - Successfully Parsed: {self.success_cases} ({self.success_cases / (total_cases) * 100:.2f}%)
                    - Failed to Parse: {self.failed_cases} ({self.failed_cases / (total_cases) * 100:.2f}%)
                - Total Collision Events Extracted: {self.total_events}
                - Time Elapsed: {(datetime.now() - self.start_time).total_seconds():.2f}s
                -------------------------"""
                )
            )

        self.running = False
        self._timer.stop()
        self.completed.emit()
