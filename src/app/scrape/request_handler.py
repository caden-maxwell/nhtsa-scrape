import logging
from time import sleep
import requests
from urllib3 import PoolManager
from urllib.parse import urlencode

from PyQt6.QtCore import QThread, pyqtSignal, QRunnable
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
        self.logger = logging.getLogger(__name__)
        self.requests = []
        self.responses = []
        self.timeout = 5
        self.pool_manager = PoolManager()

    def queue_request(self, request):
        self.requests.append(request)

    def queue_requests(self, requests):
        self.requests.extend(requests)

    def get_responses(self):
        return self.responses

    def clear(self):
        self.requests = []
        self.responses = []

    def run(self):
        with ThreadPoolExecutor() as executor:
            for request in self.requests:
                executor.submit(self.send_request, request)

    def send_request(self, request):
        response = None
        try:
            full_url = request.url + '?' + urlencode(request.params)
            response = self.pool_manager.request(request.method, full_url, headers=request.headers, timeout=self.timeout)
        except Exception as e:
            self.logger.error(e)
        self.responses.append(response)


class SearchRefreshWorker(QThread):
    refreshed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search"
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            response = requests.get(self.url, timeout=5)
            self.refreshed.emit(response.text)
        except Exception as e:
            self.logger.error(e)


class ModelUpdateWorker(QThread):
    updated = pyqtSignal(str)
    def __init__(self, make):
        super().__init__()
        self.url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/GetVehicleModels/"
        self.params= { "make": make }

    def run(self):
        try:
            response = requests.post(self.url, params=self.params, timeout=5)
            self.updated.emit(response.text)
        except Exception as e:
            self.logger.error(e)
