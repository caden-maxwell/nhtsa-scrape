from app.scrape import BaseScraper


class NassScraper(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

    def __init__(self, search_params, case_limit):
        super().__init__(search_params, case_limit)
