from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import textwrap
import time
from requests import Response

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

from app.scrape import RequestHandler, RequestQueueItem, Priority


@dataclass
class NHTSA_FIELDS:
    make: str
    model: str
    start_model_year: str
    end_model_year: str
    primary_damage: str
    secondary_damage: str
    min_dv: float
    max_dv: float


class _Meta(type(ABC), type(QObject)):
    """Metaclass for BaseScraper."""


class BaseScraper(QObject, ABC, metaclass=_Meta):
    event_parsed = pyqtSignal(dict, Response)
    started = pyqtSignal()
    completed = pyqtSignal()

    @property
    @abstractmethod
    def case_url(self) -> str:
        """Returns the URL for a specific case."""

    @property
    @abstractmethod
    def case_list_url(self) -> str:
        """Returns the URL for a list of cases."""

    @property
    @abstractmethod
    def case_url_ending(self) -> str:
        """Returns the ending of the URL for a specific case."""

    @property
    @abstractmethod
    def field_names(self) -> NHTSA_FIELDS:
        """Returns a dataclass of dropdown field names for each parameter of the scraper."""

    @abstractmethod
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._req_handler = RequestHandler()

        self.running = False
        self.start_time = 0

        self.current_page = 1
        self.success_cases = 0
        self.failed_cases = 0
        self.total_events = 0

    def start(self):
        self._req_handler.response_received.connect(self._handle_response) # This needs to be connected here instead of init to avoid running in the main thread

        self._timer = QTimer()
        self._timer.setInterval(500)  # Every 0.5 seconds
        self._timer.timeout.connect(self._check_complete)
        self._timer.start()

        self.running = True
        self.started.emit()
        self._scrape()

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
                - Time Elapsed: {time.time() - self.start_time:.2f}s
                -------------------------"""
                )
            )
        
        self.running = False
        self._timer.stop()
        self.completed.emit()
