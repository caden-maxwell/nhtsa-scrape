from PyQt6.QtCore import QThread, pyqtSignal

from . import WebRequestHandler


class SearchScrape(QThread):
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.request_handler = WebRequestHandler()
        url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search"
        self.request_handler.queue_url(url)
        self.response = None

    def run(self):
        self.request_handler.send_requests()
        self.response = self.request_handler.get_response()
        self.finished.emit()

    def get_response(self):
        return self.response
