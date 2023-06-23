import json
import logging
from math import ceil

from PyQt6.QtCore import QThread

from bs4 import BeautifulSoup

from .request_handler import WebRequestHandler, Request

class ScrapeEngine(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.CASES_PER_PAGE = 40
        self.case_limit = self.CASES_PER_PAGE
        self.image_set = "All"
        self.request_handler = WebRequestHandler()

        # Get deafult search payload
        with open("app/scrape/payload.json", "r") as f:
            self.search_payload = json.load(f)

    def update_payload(self, key, val):
        self.search_payload[key] = val
        self.logger.info(f"{key} updated to '{val}'.")

    def set_case_limit(self, limit):
        self.case_limit = limit
        self.logger.info(f"Case limit updated to '{limit}'.")
        
    def change_image_set(self, image_set):
        self.image_set = image_set
        self.logger.info(f"Image set updated to '{image_set}'.")

    def run(self):
        self.logger.debug( f"""Scrape engine started with these params:
{{
    Make: {self.search_payload['ddlMake']},
    Model: {self.search_payload['ddlModel']},
    Model Start Year: {self.search_payload['ddlStartModelYear']},
    Model End Yearj: {self.search_payload['ddlEndModelYear']},
    Min Delta V: {self.search_payload['tDeltaVFrom']},
    Max Delta V: {self.search_payload['tDeltaVTo']},
    Primary Damage: {self.search_payload['ddlPrimaryDamage']},
    Secondary Damage: {self.search_payload['lSecondaryDamage']},
    Case Limit: {self.case_limit},
    Image Set: {self.image_set}
}}"""
        )
        
        request = Request("https://crashviewer.nhtsa.dot.gov/LegacyCDS", method="POST", params=self.search_payload)
        self.request_handler.queue_request(request)
        self.request_handler.finished.connect(self.get_num_pages)
        self.request_handler.start()
        self.logger.debug("Started request handler.")

    def get_num_pages(self):
        self.request_handler.finished.disconnect(self.get_num_pages)
        response = self.request_handler.get_responses()

        if not response:
            self.logger.error("No response received.")
            return

        response = response[0]

        soup = BeautifulSoup(response.data, "html.parser")
        page_dropdown = soup.find("select", id="ddlPage")
        if not page_dropdown:
            self.logger.error("No cases found.")
            return

        num_pages = int(page_dropdown.find_all("option")[-1].text)
        max_num_pages = min(num_pages, ceil(self.case_limit / self.CASES_PER_PAGE))

        url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"
        for i in range(2, max_num_pages + 1):
            self.search_payload["currentPage"] = i
            self.request_handler.queue_request(Request(url, method="POST", params=self.search_payload))

        self.request_handler.finished.connect(self.request_cases)
        self.request_handler.start()
        self.logger.debug("Started request handler.")

    def request_cases(self):
        self.request_handler.finished.disconnect(self.request_cases)
        responses = self.request_handler.get_responses()
        self.request_handler.clear()
        self.logger.debug(f"Total responses received: {len(responses)}")

        case_urls = []
        for response in responses:
            if response.status != 200:
                self.logger.error(f"Bad response for url '{response.request_url}': {response.status}")
                continue
            if not response:
                continue
            soup = BeautifulSoup(response.data, "html.parser")
            table = soup.find_all("table")[1]
            # Get all URL links in table
            case_urls += [a["href"] for a in table.find_all("a")]
            
        if len(case_urls) > self.case_limit:
            case_urls = case_urls[:self.case_limit]

        self.request_handler.queue_requests([Request(url) for url in case_urls])
        self.request_handler.finished.connect(self.done)
        self.request_handler.start()

    def done(self):
        self.request_handler.finished.disconnect(self.done)
        responses = self.request_handler.get_responses()
        self.request_handler.clear()
        print("There are", len(responses), "cases")

    def requestInterruption(self):
        self.request_handler.requestInterruption()
        self.request_handler.wait()
        return super().requestInterruption()
