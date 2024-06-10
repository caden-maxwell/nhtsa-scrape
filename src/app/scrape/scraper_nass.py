from app.scrape import BaseScraper
from app.resources import payload_NASS


class ScraperNASS(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

    def __init__(self, search_params):
        super().__init__(search_params)

        self.search_payload = payload_NASS
        self.search_payload.update(search_params)
