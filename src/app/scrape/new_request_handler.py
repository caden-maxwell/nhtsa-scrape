import concurrent.futures
import logging
import queue
import random
import requests
import time
from PyQt6.QtCore import QObject, pyqtSignal


class Request:
    def __init__(self, url:str, method: str='GET', params:dict={}, headers:dict={}):
        self.url = url
        self.params = params
        self.method = method
        self.headers = headers

    def __str__(self):
        return f"Request(url={self.url}, method={self.method}, params={self.params}, headers={self.headers})"


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
        self.request_queue = queue.PriorityQueue()
        self.running = False
        self.rate_limit = 2.5
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.running = True
        self.started.emit()
        self.process_requests()

    def stop(self):
        self.stopped.emit()
        self.running = False

    def enqueue_request(self, request: Request, priority=9):
        self.request_queue.put((priority, request))

    def clear_queue(self, priority=-1):
        '''Clears the request queue of a certain priority. If priority is -1, clears all requests.'''
        if priority == -1:
            self.request_queue = queue.PriorityQueue()
            return

        new_queue = queue.PriorityQueue()
        while not self.request_queue.empty():
            priority, request = self.request_queue.get()
            if priority != priority:
                new_queue.put((priority, request))
        self.request_queue = new_queue
        
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

                priority, request = self.request_queue.get()
                executor.submit(self.send_request, priority, request)

                start = time.time()
                while time.time() - start < rand_time:
                    print(f"Time until next request: {rand_time - (time.time() - start):.2f}s", end="\r")
                    time.sleep(0.01)
                    print(" " * 50, end="\r")
                print(f"Waited {time.time() - start:.2f}s")

    def send_request(self, priority: int, request: Request):
        response = None
        try:
            if request.method == "GET":
                response = requests.get(request.url, params=request.params, headers=request.headers)
            elif request.method == "POST":
                response = requests.post(request.url, data=request.params, headers=request.headers)
        except Exception as e:
            self.logger.error(e)
        if response is not None:
            self.response_received.emit(priority, request.url, response.status_code, response.text, response.headers.get("Set-Cookie", ""))
