import textwrap
from time import time
from requests import Response

from PyQt6.QtCore import QThread

from app.scrape import BaseScraper, RequestQueueItem, Priority
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/CISS"

    def __init__(self, search_params):
        super().__init__()

        self.search_payload = payload_CISS
        self.search_payload.update(search_params)

    def _scrape(self):
        self.start_time = time()
        self.logger.debug(
            textwrap.dedent(
                f"""CISS Scrape Engine started with these params:
                {{
                    Make: {self.search_payload['ddlMake']},
                    Model: {self.search_payload['ddlModel']},
                    Model Start Year: {self.search_payload['ddlStartModelYear']},
                    Model End Year: {self.search_payload['ddlEndModelYear']},
                    Min Delta V: {self.search_payload['tDeltaVFrom']},
                    Max Delta V: {self.search_payload['tDeltaVTo']},
                    Primary Damage: {self.search_payload['ddlPrimaryDamage']},
                    Secondary Damage: {self.search_payload['lSecondaryDamage']},
                }}"""
            )
        )
        request = RequestQueueItem(
            self.CASE_LIST_URL,
            method="GET",
            params=self.search_payload,
            priority=Priority.CASE_LIST.value,
            callback=self._parse_case_list,
        )
        print("Sent request to CISS")
        self.req_handler.enqueue_request(request)

    def _parse_case_list(self, request: RequestQueueItem, response: Response):
        print("CISS Scraper not yet implemented.")
        self.complete()
