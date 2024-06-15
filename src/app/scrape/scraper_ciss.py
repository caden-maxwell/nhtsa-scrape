import textwrap
from time import time
from requests import Response

from app.scrape import BaseScraper, RequestQueueItem, Priority, NHTSA_FIELDS
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):

    case_url = "https://crashviewer.nhtsa.dot.gov/CISS/CISSCrashData/?crashId="
    case_list_url = "https://crashviewer.nhtsa.dot.gov/CISS"
    case_url_ending = ""

    # CISS-specific dropdown field ids
    field_names = NHTSA_FIELDS(
        make="vPICVehicleMakes",
        model="vPICVehicleModels",
        start_model_year="VehicleModelYears",
        end_model_year="VehicleModelYears",
        primary_damage="VehicleDamageImpactPlane",
        secondary_damage="VehicleDamageImpactSubSection",
        min_dv="VehicleDamageDeltaVFrom",
        max_dv="VehicleDamageDeltaVTo",
    )

    def __init__(self, search_params):
        super().__init__()

        self._payload = payload_CISS

        # Not included in requests
        # vPICVehicleMakes: [483, ],
        # vPICVehicleModels: [1945, ],
        # VehicleModelYears:  [2024 , ],

        # Already included, need to update
        # VehicleDamageImpactPlane
        # VehicleDamageImpactSubSection
        # VehicleDamagePDOFFrom
        # VehicleDamagePDOFTo
        # VehicleDamageDeltaVFrom
        # VehicleDamageDeltaVTo

        # TODO: Convert search params to CISS payload format

        self._payload.update(search_params)

    def _scrape(self):
        self.start_time = time()
        self._logger.debug(
            textwrap.dedent(
                f"""CISS Scrape Engine started with these params:
                {{
                    Make: {self._payload['ddlMake']},
                    Model: {self._payload['ddlModel']},
                    Model Start Year: {self._payload['ddlStartModelYear']},
                    Model End Year: {self._payload['ddlEndModelYear']},
                    Min Delta V: {self._payload['tDeltaVFrom']},
                    Max Delta V: {self._payload['tDeltaVTo']},
                    Primary Damage: {self._payload['ddlPrimaryDamage']},
                    Secondary Damage: {self._payload['lSecondaryDamage']},
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
