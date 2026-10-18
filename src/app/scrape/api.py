import logging
import json
from requests import Response
from bs4 import BeautifulSoup
from PyQt6.QtCore import QObject, pyqtSignal

from app.scrape.request_handler import RequestHandler, RequestQueueItem, ContextToken
from app.scrape.priority import Priority
from app.scrape.base_scraper import BaseScraper
from app.scrape.scraper_nass import ScraperNASS
from app.scrape.scraper_ciss import ScraperCISS


class APIResponseToken(ContextToken):
    parsed_ready = pyqtSignal(object)

    def __init__(self, scraper: BaseScraper):
        super().__init__()
        self.scraper = scraper


class ScraperAPI(QObject):
    def __init__(self, request_handler: RequestHandler):
        super().__init__()
        self._req_handler = request_handler

        self._logger = logging.getLogger(__name__)

    def fetch_info(self, scraper: BaseScraper):
        token = APIResponseToken(scraper)
        token.response_received.connect(lambda data: self._parse_info(data, token))

        self._req_handler.enqueue_request(
            RequestQueueItem(
                BaseScraper.ROOT + scraper.search_url,
                priority=Priority.IMMEDIATE.value,
                token=token,
            )
        )

        return token

    def _parse_info(self, response: Response, token: APIResponseToken):
        scraper = token.scraper

        soup = BeautifulSoup(response.content, "html.parser")
        options = soup.find(scraper.html_options_name, id=scraper.html_options_id)
        dropdowns: list[BeautifulSoup] = options.select("select")

        dropdown_data = {}
        for dropdown in dropdowns:
            options = dropdown.find_all("option")
            options: list[BeautifulSoup]
            dropdown_data[dropdown["name"]] = [
                (option.text, option.get("value")) for option in options
            ]

        generic_data = {
            "make": dropdown_data[scraper.field_names.make],
            "start_model_year": dropdown_data[scraper.field_names.start_model_year],
            "end_model_year": dropdown_data[scraper.field_names.end_model_year],
            "p_dmg": dropdown_data[scraper.field_names.primary_damage],
            "s_dmg": dropdown_data[scraper.field_names.secondary_damage],
        }

        token.parsed_ready.emit(generic_data)
        token.deleteLater()

    def fetch_models(self, make: str, scraper: BaseScraper) -> APIResponseToken:
        token = APIResponseToken(scraper)
        token.response_received.connect(lambda data: self._parse_models(data, token))

        makeId = 0 # TODO
        params = {"make": make} if scraper == ScraperNASS else {"makeIds": makeId}

        self._req_handler.clear_requests(Priority.IMMEDIATE)
        self._req_handler.enqueue_request(
            RequestQueueItem(
                BaseScraper.ROOT + scraper.models_url,
                params=params,
                priority=Priority.IMMEDIATE.value,
                token=token,
            )
        )

        return token

    def _parse_models(self, response: Response, token: APIResponseToken):
        model_dcts = json.loads(response.content)
        models = []
        for model in model_dcts:
            models.append((model["Value"], model["Key"]))
        models.sort()

        token.parsed_ready.emit(models)
        token.deleteLater()

    def _match_scraper(self, scraper: str) -> BaseScraper:
        match scraper:
            case "NASS" | "nass":
                return ScraperNASS
            case "CISS" | "ciss":
                return ScraperCISS
            case _:
                self._logger.error(f"Could not match name to scraper engine: {scraper}")
                