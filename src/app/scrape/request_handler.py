import concurrent.futures
import logging
import queue
import random
import requests
import time

from PyQt6.QtCore import QObject, pyqtSignal


class RequestQueueItem:
    def __init__(
        self,
        url: str,
        method: str = "GET",
        params: dict = {},
        headers: dict = {},
        priority=0,
        extra_data={},  # Additional data used to identify the request (not sent with the request)
        callback=None,
    ):
        self.url = url
        self.params = params
        self.method = method
        self.headers = headers
        self.priority = priority
        self.extra_data = extra_data
        self.callback = callback

    def __str__(self):
        return f"Request(url={self.url}, method={self.method}, params={self.params}, headers={self.headers})"

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority


class Singleton(type(QObject), type):
    """Singleton metaclass for QObjects: https://stackoverflow.com/questions/59459770/receiving-pyqtsignal-from-singleton."""

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class RequestHandler(QObject, metaclass=Singleton):
    started = pyqtSignal()
    stopped = pyqtSignal()
    response_received = pyqtSignal(RequestQueueItem, requests.Response)
    DEFAULT_MIN_RATE_LIMIT = 0.75
    DEFAULT_MAX_RATE_LIMIT = 2.50
    ABS_MIN_RATE_LIMIT = 0.2
    _instance = None

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.request_queue = queue.PriorityQueue()
        self.running = False
        self.rate_limit = 2.5
        self.ongoing_requests = []
        self.timeout = 5

        self.min_rate_limit = self.DEFAULT_MIN_RATE_LIMIT
        self.max_rate_limit = self.DEFAULT_MAX_RATE_LIMIT

    def start(self):
        self.running = True
        self.started.emit()
        self.__process_requests()

    def stop(self):
        self.stopped.emit()
        self.running = False

    def enqueue_request(self, request: RequestQueueItem):
        self.request_queue.put(request)

    def clear_queue(self, priority=-1, match_data={}):
        if priority == -1:
            self.request_queue = queue.PriorityQueue()
            return

        requests = self.request_queue.queue
        self.request_queue.queue = []
        for request in requests:
            if not self.__priority_data_match(request, priority, match_data):
                self.request_queue.put(request)

        ongoing_requests = self.ongoing_requests
        self.ongoing_requests = []
        for request in ongoing_requests:
            if not self.__priority_data_match(request, priority, match_data):
                self.ongoing_requests.append(request)

    def contains(self, priority=-1, match_data={}):
        """
        Returns True if the request queue contains requests of the given priority.
        Priority of -1 returns True if the queue is not empty.
        """
        return (
            len(self.get_queued_requests(priority, match_data)) > 0
            or len(self.get_ongoing_requests(priority, match_data)) > 0
        )

    def get_queued_requests(self, priority=-1, match_data={}):
        if priority == -1:
            return self.request_queue.queue

        queued_requests = []
        for request in self.request_queue.queue:
            if self.__priority_data_match(request, priority, match_data):
                queued_requests.append(request)
        return queued_requests

    def get_ongoing_requests(self, priority=-1, match_data={}):
        if priority == -1:
            return self.ongoing_requests

        ongoing_requests = []
        for request in self.ongoing_requests:
            if self.__priority_data_match(request, priority, match_data):
                ongoing_requests.append(request)
        return ongoing_requests

    def __priority_data_match(
        self, request: RequestQueueItem, priority: int, match_data: dict
    ):
        """Return True if the request matches the given priority and match_data, but only if match_data is not empty."""
        return request.priority == priority and (
            request.extra_data == match_data or not match_data
        )

    def update_min_rate_limit(self, value):
        self.min_rate_limit = value

    def update_max_rate_limit(self, value):
        self.max_rate_limit = value

    def __process_requests(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while self.running:
                if self.request_queue.empty():
                    time.sleep(0.1)  # Avoid busy waiting
                    continue

                # Adjust rate limit based on queue size and settings
                interval = (self.max_rate_limit - self.min_rate_limit) / 4
                if self.request_queue.qsize() <= 10:
                    self.rate_limit = self.min_rate_limit
                elif self.request_queue.qsize() <= 20:
                    self.rate_limit = self.min_rate_limit + interval
                elif self.request_queue.qsize() <= 30:
                    self.rate_limit = self.min_rate_limit + interval * 2
                elif self.request_queue.qsize() <= 40:
                    self.rate_limit = self.min_rate_limit + interval * 3
                else:
                    self.rate_limit = self.max_rate_limit

                rand_time = self.rate_limit + random.uniform(
                    -self.rate_limit / 3, self.rate_limit / 2
                )
                self.logger.debug(f"Randomized rate limit: {rand_time:.2f}s")

                request = self.request_queue.get()
                executor.submit(self.__send_request, request)

                start = time.time()
                while time.time() - start < rand_time and self.running:
                    time.sleep(0.01)  # Avoid busy waiting

    def __send_request(self, request: RequestQueueItem):
        response = None
        self.ongoing_requests.append(request)
        try:
            if request.method == "GET":
                response = requests.get(
                    request.url,
                    params=request.params,
                    headers=request.headers,
                    timeout=self.timeout,
                )
            elif request.method == "POST":
                response = requests.post(
                    request.url,
                    data=request.params,
                    headers=request.headers,
                    timeout=self.timeout,
                )
            else:
                raise ValueError(f"Invalid request method: {request.method}")
            if not response:
                raise TypeError(f"Invalid response: {response}")
            elif response.status_code != 200:
                raise ValueError(f"Invalid response code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request Exception: {e}")
            return
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            return
        finally:
            # If we clear the ongoing_requests in another thread while this request is being processed,
            # it will be removed from the list before we get here. This is fine, we just ignore the response.
            if request in self.ongoing_requests:
                self.ongoing_requests.remove(request)
            else:
                self.logger.debug(
                    f"Ignoring response for {request}, removed from ongoing requests."
                )
                return
        if response is not None and self.running:
            print(f"Response received for {request.url}")
            self.response_received.emit(request, response)
