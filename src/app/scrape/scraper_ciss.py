from app.scrape import BaseScraper
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/CISS"

    def __init__(self, search_params):
        super().__init__(search_params)

        self.search_payload = payload_CISS
        self.search_payload.update(search_params)
