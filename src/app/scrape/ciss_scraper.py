from app.scrape import BaseScraper


class CissScraper(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/CISS"

    def __init__(self, search_params, case_limit):
        super().__init__(search_params, case_limit)
