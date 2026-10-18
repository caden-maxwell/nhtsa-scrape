from dataclasses import dataclass, field
from datetime import datetime
import logging
import requests

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot, Qt


class ContextToken(QObject):
    response_received = pyqtSignal(requests.Response)


@dataclass
class _CachedResponse:
    # TODO: Fix some weird behavior is happening where expired cached responses are not getting thrown away
    COOKIE_EXPIRED_SECS = 900  # Assume site cookies expire after 15 minutes

    response: requests.Response
    created: datetime = datetime.now()

    def expired(self):
        return (datetime.now() - self.created).total_seconds() > self.COOKIE_EXPIRED_SECS


@dataclass(order=True)
class RequestQueueItem:
    url: str = field(compare=False)
    method: str = field(default="GET", compare=False)
    params: dict = field(default_factory=dict, compare=False)
    headers: dict = field(default_factory=dict, compare=False)
    priority: int = 0
    token: ContextToken = field(default=None, compare=False)
    # Additional data used to identify the request (for internal use, not sent to url)
    extra_data: dict = field(default_factory=dict, compare=False)
    callback: callable = field(default=None, compare=False)

    def __repr__(self):
        return f"RequestQueueItem(url={self.url}, priority={self.priority})"


class WorkerSignals(QObject):
    """Signals emitted by a RequestWorker instance."""

    started = pyqtSignal()
    response = pyqtSignal(RequestQueueItem, requests.Response)
    exception = pyqtSignal(Exception)


class RequestWorker(QRunnable):
    """Worker class to send requests in a separate thread."""

    def __init__(self, request: RequestQueueItem, timeout: float):
        """Create a new RequestWorker instance.

        Args:
            request (RequestQueueItem): Request to send.
            timeout (float): Request timeout in seconds.
        """
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
                params=self._request.params,
                timeout=self._timeout,
            )
        except Exception as e:
            self.signals.exception.emit(e)
        else:
            self.signals.response.emit(self._request, response)


# Create a controller class to manage the requests
class RequestHandler(QObject):
    stopped = pyqtSignal()
    response_received = pyqtSignal(RequestQueueItem, requests.Response)
    next_request = pyqtSignal()

    DEFAULT_RATE_LIMIT = 0.7  # Default rate limit in seconds
    DEFAULT_TIMEOUT = 7  # Default request timeout in seconds

    MIN_RATE_LIMIT = 0.25  # Minimum rate limit in seconds
    MIN_TIMEOUT = 0.25  # Minimum request timeout in seconds

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self._request_queue: list[RequestQueueItem] = []
        self._ongoing_requests: list[RequestQueueItem] = []
        self._response_cache: dict[str, _CachedResponse] = {}

        self._rate_limit = self.DEFAULT_RATE_LIMIT
        self._timeout = self.DEFAULT_TIMEOUT

        self._threadpool = QThreadPool()
        self._delay_timer = QTimer()
        self._delay_timer.setInterval(int(self._rate_limit * 1000))
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._start_next_request)
        # Need to use signals to avoid timer thread issues
        # Also need to use Queued connection to avoid cached responses being signaled before slot is connected
        self.next_request.connect(self._start_next_request, Qt.ConnectionType.QueuedConnection)

        self.running = True

    def stop(self):
        self.running = False
        self.stopped.emit()

    def _start_next_request(self):
        """
        Start the next request in the queue if both the rate limit and concurrent request limit are met.
        If the rate limit is not met, the delay timer is started to wait for the next request.
        """
        if self._request_queue and self.running:
            request = self._request_queue[0]
            prepared_req = requests.Request(
                method=request.method,
                url=request.url,
                params=request.params,
                headers=request.headers,
            ).prepare()

            if prepared_req.url in self._response_cache:
                cached = self._response_cache[prepared_req.url]
                if not cached.expired():
                    self._logger.debug(f"Using cached response for {prepared_req.url}.")
                    self._request_queue.remove(request)
                    self._handle_response(
                        request, self._response_cache[prepared_req.url].response, cached=True
                    )
                    return
                else:
                    self._logger.debug(f"Cached response expired for {prepared_req.url}.")

            # Check if still constrained by rate limit
            if self._delay_timer.remainingTime() > 0:
                secs = self._delay_timer.remainingTime() / 1000
                self._logger.debug(f"Need to wait {secs:.2f} seconds before next request!")
                return

            self._request_queue.remove(request)
            self._execute_request(request)

            self._start_timer()
            self._logger.debug(f"Rate limiting next request to {self._rate_limit}s")

    def _start_timer(self):
        self._delay_timer.setInterval(int(self._rate_limit * 1000))  # milliseconds
        self._delay_timer.start()

    def _execute_request(self, request: RequestQueueItem):
        """Execute a request using a RequestWorker instance.

        Args:
            request (RequestQueueItem): Request to execute.
        """

        if request.method != "GET":
            self._logger.error(f"Invalid request method: {request.method}")
            return

        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        request.headers.update(default_headers)
        self._ongoing_requests.append(request)

        runnable = RequestWorker(request, self._timeout)
        runnable.signals.response.connect(self._handle_response)
        runnable.signals.exception.connect(self._handle_exception)
        self._threadpool.start(runnable)

    def enqueue_request(self, request: RequestQueueItem):
        """Enqueue a request to be sent.

        Args:
            request (RequestQueueItem): Request to enqueue.
        """
        # Method to enqueue a request
        self._request_queue.append(request)
        self._request_queue.sort()
        self._logger.debug(f"Enqueued request for {request.url}")
        self.next_request.emit()

    def batch_enqueue(self, requests: list[RequestQueueItem]):
        """Enqueue a batch of requests to be sent. More efficient than enqueuing one request at a
        time for large numbers of requests, as the request queue will only be sorted once.

        Args:
            requests (list[RequestQueueItem]): Requests to enqueue.
        """
        urls = []
        for request in requests:
            self._request_queue.append(request)
            urls.append(request.url)
        self._request_queue.sort()

        urls_log = "\n".join(urls)
        self._logger.debug(f"Enqueued {len(requests)} requests:\n{urls_log}")

        self.next_request.emit()

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
            self._logger.debug("Cleared all requests.")
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

        self._logger.debug(
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
            if self._priority_and_data_match(request, priority, extra_data) or priority == -1
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
            if self._priority_and_data_match(request, priority, extra_data) or priority == -1
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
    def update_rate_limit(self, rate_limit):
        self._rate_limit = max(rate_limit, self.MIN_RATE_LIMIT)
        self._logger.info(f"Updated request handler min rate limit to {self._rate_limit}s.")

    @pyqtSlot(float)
    def update_timeout(self, timeout):
        self._timeout = max(timeout, self.MIN_TIMEOUT)
        self._logger.info(f"Updated request handler timeout to {self._timeout}s")

    @pyqtSlot(RequestQueueItem, requests.Response)
    def _handle_response(
        self, request: RequestQueueItem, response: requests.Response, cached: bool = False
    ):
        """Handle a response from a request worker.

        Args:
            request (RequestQueueItem): Request that was sent.
            response (requests.Response): Response received from the request.
            cached (bool): Whether the response came from the cache
        """
        if not cached:
            if request not in self._ongoing_requests:
                self._logger.debug(
                    f"Ignoring response for {request.url}, removed from ongoing requests."
                )
                return
            self._ongoing_requests.remove(request)
            self._response_cache[response.url] = _CachedResponse(response)

        if not response:
            self._logger.error(f"Failed to get response for {request.url}.")
            return

        if response.status_code != 200:
            self._logger.error(
                f"Received non-200 status code for {request.url}: {response.status_code}"
            )
            return

        if self.running:
            # New way of doing things
            request.token.response_received.emit(response)

            # Legacy; work to remove this old method
            self.response_received.emit(request, response)

    @pyqtSlot(Exception)
    def _handle_exception(self, exception: Exception):
        self._logger.error(f"Request worker exception: {exception}")
