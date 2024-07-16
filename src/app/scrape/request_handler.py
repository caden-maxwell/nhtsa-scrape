import concurrent.futures
from datetime import datetime
import logging
import queue
import random
import requests
import time
from dataclasses import dataclass, field

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


@dataclass
class _CachedResponse:
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    response: requests.Response
    created: datetime = datetime.now()

    def expired(self):
        return (
            datetime.now() - self.created
        ).total_seconds() > self.COOKIE_EXPIRED_SECS


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


class RequestHandler(QObject):
    started = pyqtSignal()
    stopped = pyqtSignal()
    response_received = pyqtSignal(RequestQueueItem, requests.Response)

    DEFAULT_MIN_RATE_LIMIT = 0.5  # Default minimum rate limit in seconds
    DEFAULT_MAX_RATE_LIMIT = 2.5  # Default maximum rate limit in seconds
    DEFAULT_TIMEOUT = 7  # Default request timeout in seconds

    ABS_MIN_RATE_LIMIT = 0.2  # Absolute minimum rate limit in seconds
    MIN_TIMEOUT = 0.1  # Minimum request timeout in seconds

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._request_queue = queue.PriorityQueue()
        self._running = False
        self._ongoing_requests = []
        self._response_cache: dict[str, _CachedResponse] = {}

        self._min_rate_limit = self.DEFAULT_MIN_RATE_LIMIT
        self._max_rate_limit = self.DEFAULT_MAX_RATE_LIMIT
        self._timeout = self.DEFAULT_TIMEOUT

    def start(self):
        self._running = True
        self.started.emit()
        self._process_requests()

    def stop(self):
        self.stopped.emit()
        self._running = False

    @pyqtSlot(RequestQueueItem)
    def enqueue_request(self, request: RequestQueueItem):
        self._request_queue.put(request)

    def clear_queue(self, priority=-1, extra_data={}):
        if priority == -1:
            self._request_queue = queue.PriorityQueue()
            return

        requests = self._request_queue.queue
        self._request_queue.queue = []
        for request in requests:
            if not self._priority_data_match(request, priority, extra_data):
                self._request_queue.put(request)

        ongoing_requests = self._ongoing_requests
        self._ongoing_requests = []
        for request in ongoing_requests:
            if not self._priority_data_match(request, priority, extra_data):
                self._ongoing_requests.append(request)

    def contains(self, priority=-1, match_data={}):
        """
        Returns True if the request queue contains requests of the given priority.
        Priority of -1 returns True if the queue is not empty.
        """
        return self.get_requests(priority, match_data) != []

    def get_requests(self, priority=-1, match_data={}) -> list[RequestQueueItem]:
        return self._get_queued_requests(
            priority, match_data
        ) + self._get_ongoing_requests(priority, match_data)

    def _get_queued_requests(self, priority=-1, extra_data={}):
        """Get queued requests with the given priority and extra data. Queued requests are requests that have not yet been sent.

        Args:
            priority (int, optional): Priority of the request. Defaults to -1, which returns all queued requests.
            extra_data (dict, optional): Extra data to match with the request. Defaults to {}.

        Returns:
            list[RequestQueueItem]: List of queued requests that match the given priority and extra data.
        """
        if priority == -1:
            return self._request_queue.queue

        queued_requests = []
        for request in self._request_queue.queue:
            if self._priority_data_match(request, priority, extra_data):
                queued_requests.append(request)
        return queued_requests

    def _get_ongoing_requests(self, priority=-1, extra_data={}):
        """Get ongoing requests with the given priority and extra data. Ongoing requests are requests that have been sent but have not yet received a response.

        Args:
            priority (int, optional): Priority of the request. Defaults to -1, which returns all ongoing requests.
            extra_data (dict, optional): Extra data to match with the request. Defaults to {}.

        Returns:
            list[RequestQueueItem]: List of ongoing requests that match the given priority and extra data.
        """
        if priority == -1:
            return self._ongoing_requests

        ongoing_requests = []
        for request in self._ongoing_requests:
            if self._priority_data_match(request, priority, extra_data):
                ongoing_requests.append(request)
        return ongoing_requests

    def _priority_data_match(
        self, request: RequestQueueItem, priority: int, extra_data: dict
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

    def _process_requests(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while self._running:
                # Process signals (e.g. update min/max rate limit)
                QApplication.processEvents()

                if self._request_queue.empty():
                    time.sleep(0.1)  # Avoid busy waiting
                    continue

                # Adjust rate limit based on queue size
                interval = (self._max_rate_limit - self._min_rate_limit) / 4
                current_rate_limit = self._min_rate_limit
                if self._request_queue.qsize() <= 10:
                    pass
                elif self._request_queue.qsize() <= 20:
                    current_rate_limit = self._min_rate_limit + interval
                elif self._request_queue.qsize() <= 30:
                    current_rate_limit = self._min_rate_limit + interval * 2
                elif self._request_queue.qsize() <= 40:
                    current_rate_limit = self._min_rate_limit + interval * 3
                else:
                    current_rate_limit = self._max_rate_limit

                # Randomize the rate limit to be 25% above or below the current rate limit
                rand_time = current_rate_limit + random.uniform(
                    -current_rate_limit / 4, current_rate_limit / 4
                )
                self._logger.debug(f"Randomized rate limit: {rand_time:.2f}s")

                request = self._request_queue.get()
                executor.submit(self._send_request, request)

                # Rate limit the requests
                start = time.time()
                while time.time() - start < rand_time and self._running:
                    time.sleep(0.05)

    def _send_request(self, request: RequestQueueItem):
        response = None

        if request.method != "GET":
            self._logger.error(f"Invalid request method: {request.method}")
            return

        prepared_request = requests.Request(
            method=request.method,
            url=request.url,
            params=request.params,
            headers=request.headers,
        ).prepare()

        # Check if the response has already been cached
        if prepared_request.url in self._response_cache:
            cached_response = self._response_cache[prepared_request.url]
            if not cached_response.expired() and self._running:
                self._logger.debug(
                    f"Using cached response for {request.url} created at {cached_response.created}"
                )
                response = cached_response.response
                self.response_received.emit(request, response)
                return

        self._ongoing_requests.append(request)
        try:
            response = requests.get(
                prepared_request.url,
                headers=prepared_request.headers,
                timeout=self._timeout,
            )
            if response.status_code != 200:
                raise ValueError(f"Invalid response code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Request Exception: {e}")
            return
        except Exception as e:
            self._logger.error(f"Exception: {e}")
            return
        finally:
            # If we clear the ongoing_requests in another thread while this request is being processed,
            # it will be removed from the list before we get here. This is fine, we just ignore the response.
            if request in self._ongoing_requests:
                self._ongoing_requests.remove(request)
            else:
                self._logger.debug(
                    f"Ignoring response for {request}, removed from ongoing requests."
                )
                return

        if response and self._running:
            self._response_cache[response.url] = _CachedResponse(response)
            self.response_received.emit(request, response)
