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


class WebRequestHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.requests = []
        self.responses = []
        self.timeout = 3.5
        self.rate_limit = 5
        self.interrupted = False

    def queue_request(self, request):
        self.requests.append(request)

    def queue_requests(self, requests):
        self.requests.extend(requests)

    def get_responses(self):
        return self.responses

    def clear(self):
        self.responses = []

    def send_requests(self):
        num_requests = len(self.requests)

        # Bracketed rate limiting: Larger # of requests = longer time between requests. Keeps load on server low.
        if num_requests <= 10:
            self.rate_limit = 0.10
        elif num_requests <= 20:
            self.rate_limit = 0.75
        elif num_requests <= 30:
            self.rate_limit = 1.50
        elif num_requests <= 40:
            self.rate_limit = 2.25
        else:
            self.rate_limit = 3.00

        if num_requests < 1:
            return
        self.logger.info(f"Sending {num_requests} request{'s'[:num_requests^1]} at 1 request per {self.rate_limit}s.")

        begin = time.time()
        reqs_sent = 0
        with ThreadPoolExecutor() as executor:
            futures = []
            for request in self.requests:
                future = executor.submit(self.send_request, request)

                # Randomize rate limit by +/- 33%
                rand_time = self.rate_limit + random.uniform(-self.rate_limit / 3, self.rate_limit / 3)
                self.logger.debug(f"Randomized rate limit: {rand_time:.2f}s")

                # Rate limiting with quick interruption response
                start = time.time()
                while time.time() - start < rand_time and not self.interrupted:
                    print(f"Time until next request: {rand_time - (time.time() - start):.2f}s", end='\r')
                    time.sleep(0.01) # Sleep for 10ms to avoid busy waiting
                    print(' '*50, end='\r')

                self.logger.info(f"Waited for {time.time() - start:.2f}s.")
                futures.append(future)
                reqs_sent += 1

                if self.interrupted:
                    self.interrupted = False
                    self.logger.debug("Request handler interrupted. Canceled further requests.")
                    break

            # Wait for all requests to finish
            for future in futures:
                future.result()

        self.logger.info(f"Sent {reqs_sent} request{'s'[:num_requests^1]} in {time.time() - begin:.2f}s.")
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
            if response.status_code != 200:
                self.logger.error(f"Request failed with status code {response.status_code}: {request}")
                return None
        except Exception as e:
            self.logger.error(e)
            return None
        self.responses.append(response)
        return response

    def stop(self):
        self.interrupted = True


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
