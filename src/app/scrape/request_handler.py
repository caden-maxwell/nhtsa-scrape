import concurrent.futures
import logging
import requests


class WebRequestHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.urls = []
        self.responses = []
        self.timeout = 5
    
    def queue_url(self, url):
        self.urls.append(url)

    def queue_urls(self, urls):
        self.urls.extend(urls)

    def get_response(self, index=0):
        if len(self.responses) > 0:
            return self.responses[index]
        return None

    def get_responses(self):
        return self.responses

    def clear(self):
        self.urls = []
        self.responses = []

    def fetch_url(self, url):
        response = None
        try:
            response = requests.get(url, timeout=self.timeout)
        except Exception as e:
            self.logger.error(e)
        self.responses.append(response)

    def send_requests(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for url in self.urls:
                executor.submit(self.fetch_url, url)
