import json
import logging
from math import ceil
from pathlib import Path

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

        # Get default search payload
        payload_path = Path(__file__).parent / "payload.json"
        with open(payload_path, "r") as f:
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
        self.request_handler.finished.connect(self.query_web_db)
        self.request_handler.start()
        self.logger.debug("Started request handler.")

    def query_web_db(self):
        self.request_handler.finished.disconnect(self.query_web_db)
        response = self.request_handler.get_responses()

        if not response:
            self.logger.error("No response received.")
            return
        
        response = response[0]
        if not response:
            self.logger.error("No response received.")
            return

        soup = BeautifulSoup(response.text, "html.parser")
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

        case_ids = []
        for response in responses:
            if response.status_code != 200:
                self.logger.error(f"Bad response for url '{response.url}': {response.status_code}")
                continue
            if not response:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find_all("table")[1]
            # Get all URL links in table
            case_urls = [a["href"] for a in table.find_all("a")]
            case_ids.extend([row.split('=')[2] for row in case_urls])
            
        if len(case_ids) > self.case_limit:
            case_ids = case_ids[:self.case_limit]

        url = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
        self.request_handler.queue_requests([Request(url + case_id) for case_id in case_ids])
        self.request_handler.finished.connect(self.cases_retrieved)
        self.request_handler.start()

    def cases_retrieved(self):
        self.request_handler.finished.disconnect(self.cases_retrieved)
        responses = self.request_handler.get_responses()
        self.request_handler.clear()
        print("There are", len(responses), "cases")

    def requestInterruption(self):
        self.request_handler.requestInterruption()
        self.request_handler.wait()
        return super().requestInterruption()
