from dataclasses import dataclass, field
from datetime import datetime
import logging
import sys
import time
import requests

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)


@dataclass
class _CachedResponse:
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    response: requests.Response
    created: datetime = datetime.now()

    def expired(self):
        return (
            datetime.now() - self.created
        ).total_seconds() > self.COOKIE_EXPIRED_SECS


@dataclass(order=True)
class RequestQueueItem:
    url: str = field(compare=False)
    method: str = field(default="GET", compare=False)
    params: dict = field(default_factory=dict, compare=False)
    headers: dict = field(default_factory=dict, compare=False)
    priority: int = 0
    # Additional data used to identify the request (for internal use, not sent to url)
    extra_data: dict = field(default_factory=dict, compare=False)
    callback: callable = field(default=None, compare=False)

    def __repr__(self):
        return f"RequestQueueItem(url={self.url}, priority={self.priority})"


class WorkerSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal(RequestQueueItem, requests.Response)


# Define a worker class that inherits QObject
class RequestWorker(QRunnable):
    def __init__(self, request: RequestQueueItem, timeout: float):
        super().__init__()
        self._request = request
        self._timeout = timeout
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signals.started.emit()
        response = None
        try:
            response = requests.get(
                url=self._request.url,
                headers=self._request.headers,
                timeout=self._timeout,
            )
        except Exception as e:
            print(f"Failed to get response for {self._request.url}: {e}")

        self.signals.finished.emit(self._request, response)


# Create a controller class to manage the requests
class RequestController(QObject):
    stopped = pyqtSignal()
    response_received = pyqtSignal(RequestQueueItem, requests.Response)
    display_string = pyqtSignal(str)

    DEFAULT_MIN_RATE_LIMIT = 0.5  # Minimum delay between requests
    DEFAULT_MAX_RATE_LIMIT = 2.5  # Maximum delay between requests
    DEFAULT_TIMEOUT = 7  # Default timeout for requests
    MAX_CONCURRENT_REQUESTS = -1  # Maximum number of concurrent requests

    ABS_MIN_RATE_LIMIT = 0.25
    MIN_TIMEOUT = 0.5

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._request_queue: list[RequestQueueItem] = []
        self._ongoing_requests: list[RequestQueueItem] = []
        self._response_cache: dict[str, _CachedResponse] = {}

        self._min_rate_limit = self.DEFAULT_MIN_RATE_LIMIT
        self._max_rate_limit = self.DEFAULT_MAX_RATE_LIMIT
        self._timeout = self.DEFAULT_TIMEOUT

        self._threadpool = QThreadPool()
        self._delay_timer = QTimer()
        self._delay_timer.setInterval(int(self.DEFAULT_MIN_RATE_LIMIT * 1000))
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._start_next_request)

        self.running = True

    def stop(self):
        self.running = False
        self.stopped.emit()

    def _start_next_request(self):
        """Start the next request in the queue if both the rate limit and concurrent request limit are met.
        If the rate limit is not met, the delay timer is started to wait for the next request.
        """
        if self._request_queue and self.running:

            # if the next request's response is cached, we can use it immediately
            request = self._request_queue[0]
            prepared_req = requests.Request(
                method=request.method,
                url=request.url,
                params=request.params,
                headers=request.headers,
            ).prepare()
            request.url = prepared_req.url

            if request.url in self._response_cache:
                cached = self._response_cache[request.url]
                if not cached.expired():
                    self.display_string.emit(f"Using cached response for {request.url}")
                    self._process_response(
                        request, self._response_cache[request.url].response
                    )
                    self._request_queue.remove(request)
                    return
            # If not in cache, perform additional checks

            # Check if the rate limit is met
            if self._delay_timer.remainingTime() > 0:
                self.display_string.emit(
                    f"Need to wait {self._delay_timer.remainingTime()/1000:.2f} seconds before next request"
                )
                return

            # Check if the maximum concurrent requests limit is met
            if (
                self._threadpool.activeThreadCount() >= self.MAX_CONCURRENT_REQUESTS
                and self.MAX_CONCURRENT_REQUESTS != -1
            ):
                self.display_string.emit(
                    "Maximum concurrent requests reached. Waiting..."
                )
                self._delay_timer.start()
                return

            # Start the next request
            request = self._request_queue.pop(0)
            self._execute_request(request)

            self._delay_timer.start()

    def _execute_request(self, request: RequestQueueItem):
        """Execute a request using a RequestWorker instance.

        Args:
            request (RequestQueueItem): Request to execute.
        """

        if request.method != "GET":
            self.display_string.emit(f"Invalid request method: {request.method}")
            return

        request.headers.update({"User-Agent": "Mozilla/5.0"})
        self._ongoing_requests.append(request)

        runnable = RequestWorker(request, self._timeout)
        runnable.signals.finished.connect(self._handle_response)
        runnable.signals.started.connect(
            lambda: self.display_string.emit(
                f"<b>Starting request for {request.url}<b>"
            )
        )
        self._threadpool.start(runnable)

    def enqueue_request(self, request: RequestQueueItem):
        """Enqueue a request to be sent.

        Args:
            request (RequestQueueItem): Request to enqueue.
        """
        # Method to enqueue a request
        self._request_queue.append(request)
        self._request_queue.sort()
        self.display_string.emit(f"Enqueued request for {request.url}")
        self._start_next_request()

    def contains_requests(self, priority=-1, extra_data={}):
        """Check if the request queue or ongoing requests contains any requests with the given priority and extra data.

        Args:
            priority (int, optional): Priority of the requests to check. Defaults to -1.
            extra_data (dict, optional): Extra data to match with each request. Defaults to {}.

        Returns:
            bool: True if the request queue or ongoing requests contains any requests with the given priority and extra data.
        """
        return any(self.get_requests(priority, extra_data))

    def get_requests(self, priority=-1, extra_data={}):
        """Get requests with the given priority and extra data. If no priority is given, all requests are returned.

        Args:
            priority (int, optional): Priority of the requests to get. Defaults to -1.
            extra_data (dict, optional): Extra data to match with each request. Defaults to {}.

        Returns:
            tuple[list[RequestQueueItem], list[RequestQueueItem]]: Tuple of queued and ongoing requests matching the params.
        """
        queued = self._get_queued_requests(priority, extra_data)
        ongoing = self._get_ongoing_requests(priority, extra_data)
        return queued, ongoing

    def clear_requests(self, priority=-1, extra_data={}):
        if priority == -1:
            self._request_queue.clear()
            self._ongoing_requests.clear()
            self.display_string.emit("Cleared all requests.")
            return

        self._request_queue = [
            request
            for request in self._request_queue
            if not self._priority_and_data_match(request, priority, extra_data)
        ]
        self._request_queue.sort()

        self._ongoing_requests = [
            request
            for request in self._ongoing_requests
            if not self._priority_and_data_match(request, priority, extra_data)
        ]

        self.display_string.emit(
            f"Cleared requests with priority {priority} and extra data {extra_data}."
        )

    def _get_queued_requests(self, priority=-1, extra_data={}):
        """Get queued requests with the given priority and extra data. Queued requests are requests that have not yet been sent.

        Args:
            priority (int, optional): Priority of the request. Defaults to -1, which returns all queued requests.
            extra_data (dict, optional): Extra data to match with the request. Defaults to {}.
            opposite (bool, optional): If True, returns requests that expicitly do not match the given priority and extra data. Defaults to False.

        Returns:
            list[RequestQueueItem]: List of queued requests that match the given priority and extra data.
        """
        return [
            request
            for request in self._request_queue
            if self._priority_and_data_match(request, priority, extra_data)
            or priority == -1
        ]

    def _get_ongoing_requests(self, priority=-1, extra_data={}):
        """Get ongoing requests with the given priority and extra data. Ongoing requests are requests that have been sent but have not yet received a response.

        Args:
            priority (int, optional): Priority of the request. Defaults to -1, which returns all ongoing requests.
            extra_data (dict, optional): Extra data to match with the request. Defaults to {}.

        Returns:
            list[RequestQueueItem]: List of ongoing requests that match the given priority and extra data.
        """
        return [
            request
            for request in self._ongoing_requests
            if self._priority_and_data_match(request, priority, extra_data)
            or priority == -1
        ]

    def _priority_and_data_match(
        self, request: RequestQueueItem, priority: int = -1, extra_data: dict = {}
    ):
        """Check if the request matches the given priority and extra data.

        Args:
            request (RequestQueueItem): Request to check.
            priority (int): Priority to match.
            extra_data (dict): Extra data to match with requests. If empty, only the priority
                is checked. Every key-value pair must match a request's extra_data,
                but the request's actual extra_data may have additional keys.

        Returns:
            bool: True if the request matches the given priority and extra data.
        """
        if request.priority != priority:
            return False

        for key, value in extra_data.items():
            if key not in request.extra_data or request.extra_data[key] != value:
                return False

        return True

    @pyqtSlot(float)
    def update_min_rate_limit(self, min_rate_limit):
        self._min_rate_limit = max(min_rate_limit, self.ABS_MIN_RATE_LIMIT)
        self._logger.debug(
            f"Successfully updated request handler min rate limit to {self._min_rate_limit}s."
        )

    @pyqtSlot(float)
    def update_max_rate_limit(self, max_rate_limit):
        self._max_rate_limit = max(max_rate_limit, self._min_rate_limit)
        self._logger.debug(
            f"Successfully updated request handler max rate limit to {self._max_rate_limit}s."
        )

    @pyqtSlot(float)
    def update_timeout(self, timeout):
        self._timeout = max(timeout, self.MIN_TIMEOUT)
        self._logger.debug(
            f"Successfully updated request handler timeout to {self._timeout}s"
        )

    @pyqtSlot(RequestQueueItem, requests.Response)
    def _handle_response(self, request: RequestQueueItem, response: requests.Response):
        """Handle a response from a request worker.

        Args:
            request (RequestQueueItem): Request that was sent.
            response (requests.Response): Response received from the request.
        """
        if request not in self._ongoing_requests:
            self.display_string.emit(
                f"Ignoring response for {request.url}, removed from ongoing requests."
            )
            return

        self._ongoing_requests.remove(request)
        self._process_response(request, response)

    def _process_response(self, request: RequestQueueItem, response: requests.Response):
        """Process a response from a request worker or the cache.

        Args:
            request (RequestQueueItem): Request that was sent.
            response (requests.Response): Response received from the request.
        """
        if not response:
            self.display_string.emit(f"Failed to get response for {request.url}.")
            return

        if response.status_code != 200:
            self.display_string.emit(
                f"Received non-200 status code for {request.url}: {response.status_code}"
            )
            return

        # Cache and emit the response
        if self.running:
            self._response_cache[response.url] = _CachedResponse(response)
            self.response_received.emit(request, response)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Controller instance
        self.controller = RequestController()
        self.controller.display_string.connect(self.display_string)
        self.controller.response_received.connect(self.display_response)

        self.initUI()
        self.start_time = time.time()

    def initUI(self):
        self.setWindowTitle("Concurrent Requests Example")
        self.setGeometry(100, 100, 600, 400)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Text Edit for displaying responses
        self.response_textedit = QTextEdit()
        layout.addWidget(self.response_textedit)

        req_btn_layout = QHBoxLayout()

        # Buttons for requesting data
        request_btn = QPushButton("Request Data")
        request_btn.clicked.connect(self.request_data_clicked)
        req_btn_layout.addWidget(request_btn)

        request_btn_2 = QPushButton("Request Data (2)")
        request_btn_2.clicked.connect(self.request_data_clicked_2)
        req_btn_layout.addWidget(request_btn_2)

        layout.addLayout(req_btn_layout)

        action_btn_layout = QHBoxLayout()

        get_requests_btn = QPushButton("Get Requests")
        get_requests_btn.clicked.connect(self.display_requests)
        action_btn_layout.addWidget(get_requests_btn)

        clear_requests_btn = QPushButton("Clear Requests")
        clear_requests_btn.clicked.connect(
            lambda: self.controller.clear_requests(0)
        )  # Clear requests with priority 0
        action_btn_layout.addWidget(clear_requests_btn)

        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.response_textedit.clear)
        action_btn_layout.addWidget(clear_button)

        layout.addLayout(action_btn_layout)

    def request_data_clicked(self):
        url = "https://jsonplaceholder.typicode.com/posts/1"
        self.controller.enqueue_request(
            RequestQueueItem(
                url=url,
                callback=self.display_response,
                priority=0,
            )
        )

    def request_data_clicked_2(self):
        url = "https://jsonplaceholder.typicode.com/posts/2"
        self.controller.enqueue_request(
            RequestQueueItem(
                url=url,
                callback=self.display_response,
                priority=1,
            )
        )

    def display_requests(self):
        """Gets all queued and ongoing requests from the controller."""
        queued, ongoing = self.controller.get_requests()
        self.display_string("--- Requests ---")
        self.display_string("Queued requests:")
        for request in queued:
            self.display_string(request.url)

        self.display_string("Ongoing requests:")
        for request in ongoing:
            self.display_string(request.url)
        self.display_string("--- End of Requests ---")

    def display_string(self, string):
        now = time.time() - self.start_time
        self.response_textedit.append(f"{now:.2f}: {string}")

    def display_response(self, request: RequestQueueItem, response: requests.Response):
        now = time.time() - self.start_time
        self.response_textedit.append(
            f"<b>{now:.2f}: Received response: {response.text}<b>"
        )


# Main function to run the application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
