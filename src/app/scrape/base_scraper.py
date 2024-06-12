import logging
import textwrap
import time
from requests import Response

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from app.scrape import RequestHandler, RequestQueueItem, Priority


class BaseScraper(QObject):
    event_parsed = pyqtSignal(dict, Response)
    started = pyqtSignal()
    completed = pyqtSignal()
    CASE_URL = None  # Define in child classes
    CASE_LIST_URL = None  # Define in child classes

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.__handle_response)
        self.search_payload = {}  # Define in child classes

        self.running = False
        self.start_time = 0

        self.current_page = 1
        self.success_cases = 0
        self.failed_cases = 0
        self.total_events = 0

    def start(self):
        self.running = True
        self.started.emit()
        self._scrape()

    def _scrape(self):
        raise NotImplementedError

    @pyqtSlot(RequestQueueItem, Response)
    def __handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.CASE_LIST.value
            or request.priority == Priority.CASE.value
        ):
            print("Response handled by", self.__class__.__name__, "with Callback", request.callback)
            request.callback(request, response)

    def complete(self):
        # Order matters here, otherwise the request handler will start making
        # unnecessary case list requests once the individual cases are cleared
        self.req_handler.clear_queue(Priority.CASE_LIST.value)
        self.req_handler.clear_queue(Priority.CASE.value)

        if self.success_cases + self.failed_cases < 1:
            self.logger.info("No data was found. Scrape complete.")
        else:
            total_cases = self.success_cases + self.failed_cases
            self.logger.info(
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
        self.completed.emit()
        self.running = False
