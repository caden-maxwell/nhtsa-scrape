import concurrent.futures
import logging
import queue
import random
import requests
import time
from PyQt6.QtCore import QObject, pyqtSignal


class Request:
    def __init__(self, url:str, method: str='GET', params:dict={}, headers:dict={}, priority=0):
        self.url = url
        self.params = params
        self.method = method
        self.headers = headers
        self.priority = priority

    def __str__(self):
        return f"Request(url={self.url}, method={self.method}, params={self.params}, headers={self.headers})"

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

class Singleton(type(QObject), type):
    '''Singleton metaclass for QObjects: https://stackoverflow.com/questions/59459770/receiving-pyqtsignal-from-singleton.'''
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
    response_received = pyqtSignal(int, str, int, str, str)
    _instance = None

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.request_queue = queue.PriorityQueue()
        self.running = False
        self.rate_limit = 2.5
        self.ongoing_requests = []

    def start(self):
        self.running = True
        self.started.emit()
        self.process_requests()

    def stop(self):
        self.stopped.emit()
        self.running = False

    def enqueue_request(self, request: Request):
        self.request_queue.put(request)

    def clear_queue(self, priority=-1):
        if priority == -1:
            self.request_queue = queue.PriorityQueue()
            return

        requests = self.request_queue.queue
        self.request_queue.queue = []
        for request in requests:
            if request.priority != priority:
                self.request_queue.put(request)

    def contains(self, priority=-1):
        '''
        Returns True if the request queue contains requests of the given priority.
        Priority of -1 returns True if the queue is not empty.
        '''
        if priority == -1:
            return not self.request_queue.empty()

        for request in self.request_queue.queue:
            if request.priority == priority:
                return True
        return False

    def get_ongoing_requests(self, priority=-1):
        if priority == -1:
            return self.ongoing_requests
        
        ongoing_requests = []
        for request in self.ongoing_requests:
            if request.priority == priority:
                ongoing_requests.append(request)
        return ongoing_requests

    def process_requests(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while self.running:
                if self.request_queue.empty():
                    time.sleep(0.1)
                    continue

                if self.request_queue.qsize() <= 10:
                    self.rate_limit = 0.70
                elif self.request_queue.qsize() <= 20:
                    self.rate_limit = 0.85
                elif self.request_queue.qsize() <= 30:
                    self.rate_limit = 1.70
                else:
                    self.rate_limit = 3.40

                # Randomize rate limit by +/- 33%
                rand_time = self.rate_limit + random.uniform(-self.rate_limit / 3, self.rate_limit / 2)
                self.logger.debug(f"Randomized rate limit: {rand_time:.2f}s")

                request = self.request_queue.get()
                executor.submit(self.send_request, request)

                start = time.time()
                while time.time() - start < rand_time:
                    time.sleep(0.01)

    def send_request(self, request: Request):
        response = None
        self.ongoing_requests.append(request)
        try:
            if request.method == "GET":
                response = requests.get(request.url, params=request.params, headers=request.headers)
            elif request.method == "POST":
                response = requests.post(request.url, data=request.params, headers=request.headers)
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
        self.ongoing_requests.remove(request)
        if response is not None:
            self.response_received.emit(request.priority, request.url, response.status_code, response.text, response.headers.get("Set-Cookie", ""))
