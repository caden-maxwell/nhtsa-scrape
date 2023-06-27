import logging
import random
import requests
import time

from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor


class Request:
    def __init__(self, url, method='GET', params={}, headers={}):
        self.url = url
        self.params = params
        self.method = method
        self.headers = headers

    def __str__(self):
        return f"Request(url={self.url}, method={self.method}, params={self.params}, headers={self.headers})"


class WebRequestHandler(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.requests = []
        self.responses = []
        self.timeout = 5
        self.rate_limit = 5

    def queue_request(self, request):
        self.requests.append(request)

    def queue_requests(self, requests):
        self.requests.extend(requests)

    def get_responses(self):
        return self.responses

    def clear(self):
        self.responses = []

    def run(self):
        num_requests = len(self.requests)

        # Bracketed rate limiting: Larger # of requests = longer time between requests. Keeps load on server low.
        if num_requests <= 10:
            self.rate_limit = 0.25
        elif num_requests <= 20:
            self.rate_limit = 1
        elif num_requests <= 30:
            self.rate_limit = 1.75
        elif num_requests <= 40:
            self.rate_limit = 2.5
        elif num_requests <= 50:
            self.rate_limit = 3.25
        else:
            self.rate_limit = 4

        self.logger.info(f"Sending {num_requests} request{'s'[:num_requests^1]} at 1 request per {self.rate_limit}s.")

        with ThreadPoolExecutor() as executor:
            for request in self.requests:
                future = executor.submit(self.send_request, request)

                # Randomize rate limit by +/- 33%
                rand_time = self.rate_limit + random.uniform(-self.rate_limit / 3, self.rate_limit / 3)
                self.logger.debug(f"Randomized rate limit: {rand_time:.2f}s")

                # Rate limiting with quick interruption response
                start = time.time()
                while time.time() - start < rand_time and not self.isInterruptionRequested():
                    time.sleep(0.01)

                if self.isInterruptionRequested():
                    self.logger.debug("Request handler interrupted. Stopping thread.")
                    future.cancel()
                    break

                self.responses.append(future.result())
        self.requests = []

    def send_request(self, request: Request):
        response = None
        try:
            if request.method == 'GET':
                response = requests.get(request.url, params=request.params, headers=request.headers, timeout=self.timeout)
            elif request.method == 'POST':
                response = requests.post(request.url, params=request.params, headers=request.headers, timeout=self.timeout)
            else:
                self.logger.error(f"Invalid request method: {request.method}")
        except Exception as e:
            self.logger.error(e)
        return response


class SearchRefreshWorker(QThread):
    retrieved = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search"
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            response = requests.get(self.url, timeout=5)
            self.retrieved.emit(response.text)
        except Exception as e:
            self.logger.error(e)


class ModelUpdateWorker(QThread):
    updated = pyqtSignal(str)
    def __init__(self, make):
        super().__init__()
        self.url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/"
        self.params= { "make": make }
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            response = requests.post(self.url, params=self.params, timeout=5)
            self.updated.emit(response.text)
        except Exception as e:
            self.logger.error(e)
