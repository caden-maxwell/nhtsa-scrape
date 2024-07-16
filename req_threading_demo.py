# This is a simple example of how I could improve the existing RequestHandler class


from dataclasses import dataclass, field
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
class RequestQueueItem:
    url: str
    method: str = "GET"
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    priority: int = 0
    # Additional data used to identify the request (for internal use, not sent to url)
    extra_data: dict = field(default_factory=dict)
    callback: callable = None

    def __lt__(self, other: "RequestQueueItem"):
        return self.priority < other.priority

    def __eq__(self, other: "RequestQueueItem"):
        return self.priority == other.priority


class WorkerSignals(QObject):
    started = pyqtSignal()
    response_received = pyqtSignal(RequestQueueItem, requests.Response)


# Define a worker class that inherits QObject
class RequestWorker(QRunnable):
    def __init__(self, request: RequestQueueItem):
        super().__init__()
        self.request = request
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.signals.started.emit()
        response = requests.get(self.request.url)
        time.sleep(3)  # Simulate some processing time
        self.signals.response_received.emit(self.request, response)


# Create a controller class to manage the requests
class RequestController(QObject):
    MIN_RATE_LIMIT = 1  # Minimum delay between requests (500 ms)
    MAX_RATE_LIMIT = 1  # Maximum number of requests per second
    MAX_CONCURRENT_REQUESTS = -1  # Maximum number of concurrent requests
    display_string = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.delay_timer = QTimer()
        self.delay_timer.setInterval(int(self.MIN_RATE_LIMIT * 1000))
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.start_next_request)
        self.request_queue: list[RequestQueueItem] = []
        self.ongoing_requests: list[RequestQueueItem] = []

    def start_next_request(self):
        """Start the next request in the queue if both the rate limit and concurrent request limit are met."""
        if self.request_queue:
            if self.delay_timer.remainingTime() > 0:
                self.display_string.emit(
                    f"Need to wait {self.delay_timer.remainingTime()/1000:.2f} seconds before next request"
                )
                return

            if (
                self.threadpool.activeThreadCount() >= self.MAX_CONCURRENT_REQUESTS
                and self.MAX_CONCURRENT_REQUESTS != -1
            ):
                self.display_string.emit(
                    "Maximum concurrent requests reached. Waiting..."
                )
                self.delay_timer.start()
                return

            request = self.request_queue.pop(0)
            self.ongoing_requests.append(request)
            self.display_string.emit(f"Executing worker for {request.url}")
            self.execute_request(request)

            self.delay_timer.start()

    def execute_request(self, request: RequestQueueItem):
        # Method to execute a request
        runnable = RequestWorker(request)
        runnable.signals.response_received.connect(self.handle_callback)
        runnable.signals.started.connect(
            lambda: self.display_string.emit(
                f"<b>Starting request for {request.url}<b>"
            )
        )
        self.threadpool.start(runnable)

    def enqueue_request(self, request: RequestQueueItem):
        # Method to enqueue a request
        self.request_queue.append(request)
        self.display_string.emit(f"Enqueued request for {request.url}")
        self.start_next_request()

    @pyqtSlot(RequestQueueItem, requests.Response)
    def handle_callback(self, request: RequestQueueItem, response: requests.Response):
        self.ongoing_requests.remove(request)
        request.callback(response)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # Controller instance
        self.controller = RequestController()
        self.controller.display_string.connect(self.display_string)

        button_layout = QHBoxLayout()

        # Buttons for requesting data
        request_btn = QPushButton("Request Data")
        request_btn.clicked.connect(self.request_data_clicked)
        button_layout.addWidget(request_btn)

        get_requests_btn = QPushButton("Get Requests")
        get_requests_btn.clicked.connect(self.get_requests)
        button_layout.addWidget(get_requests_btn)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.response_textedit.clear)
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

    def request_data_clicked(self):
        url = "https://jsonplaceholder.typicode.com/posts/1"
        self.controller.enqueue_request(
            RequestQueueItem(
                url=url,
                callback=self.display_response,
            )
        )

    def get_requests(self):
        """Gets all queued and ongoing requests from the controller."""
        self.display_string("--- Requests ---")
        self.display_string("Queued requests:")
        for url, _ in self.controller.request_queue:
            self.display_string(url)

        self.display_string("Ongoing requests:")
        for url in self.controller.ongoing_requests:
            self.display_string(url)
        self.display_string("--- End of Requests ---")

    def display_string(self, string):
        now = time.time() - self.start_time
        self.response_textedit.append(f"{now:.2f}: {string}")

    def display_response(self, response: requests.Response):
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
