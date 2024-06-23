from datetime import datetime
import textwrap
from bs4 import BeautifulSoup
from requests import Response

from app.scrape import BaseScraper, RequestQueueItem, Priority, ScrapeParams
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):

    search_url = "/CISS/SearchFilter"
    models_url = "/SCI/GetvPICVehicleModelbyMake/"
    case_url = "/CISS/Details?Study=CISS&CaseId={case_id}"
    case_url_raw = "/CISS/CISSCrashData?crashId={case_id}"
    case_list_url = "/CISS/Index"
    img_url = "/cases/photo/?photoid={img_id}"

    # CISS-specific dropdown field ids
    field_names = ScrapeParams[str](
        make="vPICVehicleMakes",
        model="vPICVehicleModels",
        start_model_year="VehicleModelYears",
        end_model_year="VehicleModelYears",
        primary_damage="VehicleDamageImpactPlane",
        secondary_damage="VehicleDamageImpactSubSection",
        min_dv="VehicleDamageDeltaVFrom",
        max_dv="VehicleDamageDeltaVTo",
    )

    def __init__(self, params: ScrapeParams[int]):
        super().__init__()

        self._payload = payload_CISS.copy()
        self._payload.update(self._convert_params_to_payload(params))

    def _convert_params_to_payload(self, params: ScrapeParams[int]) -> dict:
        # The CISS payload requires a list of years as opposed to a range between two years,
        # so we need to convert the range to a list, but only if the years are valid.
        # Some of the possible year options are 9999, 9998, and -1, which are not valid years.

        min_year = 1920  # The earliest year available in the dropdown # TODO: Kinda a magic number
        max_year = datetime.now().year
        start_year = (
            params.start_model_year
            if min_year <= params.start_model_year <= max_year
            else min_year
        )
        end_year = (
            params.end_model_year
            if min_year <= params.end_model_year <= max_year
            else max_year
        )

        # If the range is the entire range of years, we can just leave the list empty
        if start_year == min_year and end_year == max_year:
            start_year = end_year + 1
        # If the length of the range is greater than 50 years, limit the range to 50 years to avoid site exception
        elif end_year - start_year > 50:
            start_year = end_year - 50
            self._logger.warning(
                "A model range of over 50 years will result in an error on the CISS website. The range has been limited to 50 years."
            )

        payload = {
            self.field_names.make: [params.make],
            self.field_names.start_model_year: list(range(start_year, end_year + 1)),
            self.field_names.primary_damage: (
                params.primary_damage if params.primary_damage != -1 else ""
            ),
            self.field_names.secondary_damage: (
                params.secondary_damage if params.secondary_damage != -1 else ""
            ),
            self.field_names.min_dv: params.min_dv if params.min_dv != 0 else "",
            self.field_names.max_dv: params.max_dv if params.max_dv != 0 else "",
        }

        if params.model != -1:
            payload[self.field_names.model] = [params.model]

        return payload

    def _scrape(self):
        self._logger.debug(
            textwrap.dedent(
                f"""{self.__class__.__name__} started with these params:
                {{
                    Make: {self._payload[self.field_names.make]},
                    Model: {self._payload.get(self.field_names.model, "ALL")},
                    Model Years: {self._payload[self.field_names.start_model_year]},
                    Min Delta V: {self._payload[self.field_names.min_dv]},
                    Max Delta V: {self._payload[self.field_names.max_dv]},
                    Primary Damage: {self._payload[self.field_names.primary_damage]},
                    Secondary Damage: {self._payload[self.field_names.secondary_damage]},
                }}"""
            )
        )

        self._req_case_list()

    def _req_case_list(self):
        self._req_handler.enqueue_request(
            RequestQueueItem(
                self.ROOT + self.case_list_url,
                method="GET",
                params=self._payload,
                priority=Priority.CASE_LIST.value,
                callback=self._parse_case_list,
                extra_data={"database": "CISS"},
            )
        )


    def _handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.CASE_LIST.value
            or request.priority == Priority.CASE.value
        ) and request.extra_data.get("database") == "CISS":
            request.callback(request, response)

    def _parse_case_list(self, request: RequestQueueItem, response: Response):
        if not self.running:
            return

        if not response.content:
            self._logger.error(
                f"Received empty response from {request.url}. Ending scrape..."
            )
            return

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find(
            "table",
            {"class": "display table table-condensed table-striped table-hover"},
        )
        case_ids = []
        if table:
            urls = [a["href"] for a in table.find_all("a")]
            case_ids = [int(url.split("=")[-1]) for url in urls]

        if not case_ids:
            self._logger.debug(
                f"No cases found on page {self._payload['currentPage']}. Scrape complete."
            )
            return

        self._logger.info(
            f"Requesting {len(case_ids)} case{'s'[:len(case_ids)^1]} from page {self.current_page}..."
        )

        for case_id in case_ids:
            self._req_handler.enqueue_request(
                RequestQueueItem(
                    self.ROOT + self.case_url_raw.format(case_id=case_id),
                    priority=Priority.CASE.value,
                    callback=self.__parse_case,
                    extra_data={"database": "CISS"},
                )
            )

        self.current_page += 1
        self._payload["currentPage"] = self.current_page
        self._logger.debug(f"Queueing page {self.current_page}...")

        self._req_case_list()

    def __parse_case(self, request: RequestQueueItem, response: Response):
        print("NOT IMPLEMENTED YET")