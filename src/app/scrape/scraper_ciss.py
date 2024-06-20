from datetime import datetime
import textwrap
from requests import Response

from app.scrape import BaseScraper, RequestQueueItem, Priority, ScrapeParams
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):

    case_url = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId="
    case_list_url = "https://crashviewer.nhtsa.dot.gov/CISS/Index"
    case_url_ending = ""

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

        self._payload = payload_CISS
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

        return {
            self.field_names.make: [params.make],
            self.field_names.model: [params.model],
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

    def _scrape(self):
        self._logger.debug(
            textwrap.dedent(
                f"""{self.__class__.__name__} started with these params:
                {{
                    Make: {self._payload[self.field_names.make]},
                    Model: {self._payload[self.field_names.model]},
                    Model Years: {self._payload[self.field_names.start_model_year]},
                    Min Delta V: {self._payload[self.field_names.min_dv]},
                    Max Delta V: {self._payload[self.field_names.max_dv]},
                    Primary Damage: {self._payload[self.field_names.primary_damage]},
                    Secondary Damage: {self._payload[self.field_names.secondary_damage]},
                }}"""
            )
        )

        request = RequestQueueItem(
            self.case_list_url,
            method="GET",
            params=self._payload,
            priority=Priority.CASE_LIST.value,
            callback=self._parse_case_list,
            extra_data={"database": "CISS"},
        )
        self._req_handler.enqueue_request(request)

    def _handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.CASE_LIST.value
            or request.priority == Priority.CASE.value
        ) and request.extra_data.get("database") == "CISS":
            request.callback(request, response)

    def _parse_case_list(self, request: RequestQueueItem, response: Response):
        print("CISS Scraper not yet implemented.")
        self.complete()
