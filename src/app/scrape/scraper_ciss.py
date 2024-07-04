from datetime import datetime
import textwrap
from bs4 import BeautifulSoup
from requests import Response
import json
from collections import defaultdict, namedtuple
from fuzzywuzzy import fuzz

from app.scrape import BaseScraper, RequestQueueItem, Priority, FieldNames
from app.resources import payload_CISS


class ScraperCISS(BaseScraper):

    search_url = "/CISS/SearchFilter"
    models_url = "/SCI/GetvPICVehicleModelbyMake/"
    case_url = "/CISS/Details?Study=CISS&CaseId={case_id}"
    case_url_raw = "/CISS/CISSCrashData?crashId={case_id}"
    case_list_url = "/CISS/Index"
    img_url = "/cases/photo/?photoid={img_id}"
    _fuzz_threshold = 90

    # CISS-specific dropdown field ids
    field_names = FieldNames(
        make="vPICVehicleMakes",
        model="vPICVehicleModels",
        start_model_year="VehicleModelYears",
        end_model_year="VehicleModelYears",
        primary_damage="VehicleDamageImpactPlane",
        secondary_damage="VehicleDamageImpactSubSection",
        min_dv="VehicleDamageDeltaVFrom",
        max_dv="VehicleDamageDeltaVTo",
    )

    def __init__(
        self,
        make,
        model,
        start_model_year,
        end_model_year,
        primary_damage,
        secondary_damage,
        min_dv,
        max_dv,
    ):
        super().__init__()

        self._payload = payload_CISS.copy()

        # Named tuple to store the text and value of a dropdown option
        Option = namedtuple("Param", ["text", "value"])

        self._make = Option(*make)
        self._model = Option(*model)
        self._start_model_year = Option(*start_model_year)
        self._end_model_year = Option(*end_model_year)
        self._primary_damage = Option(*primary_damage)
        self._secondary_damage = Option(*secondary_damage)
        self._min_dv = min_dv
        self._max_dv = max_dv

        # The CISS payload requires a list of years as opposed to a range between two years,
        # so we need to convert the range to a list, but only if the years are valid.
        # Some of the possible year options are 9999, 9998, and -1, which are not valid years.

        min_year = 1920  # The earliest year available in the dropdown # TODO: Kinda a magic number
        max_year = datetime.now().year
        start_year = (
            self._start_model_year.value
            if min_year <= self._start_model_year.value <= max_year
            else min_year
        )
        end_year = (
            self._end_model_year.value
            if min_year <= self._end_model_year.value <= max_year
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
            self.field_names.make: [self._make.value],
            self.field_names.start_model_year: list(range(start_year, end_year + 1)),
            self.field_names.primary_damage: (
                self._primary_damage.value if self._primary_damage.value != -1 else ""
            ),
            self.field_names.secondary_damage: (
                self._secondary_damage if self._secondary_damage.value != -1 else ""
            ),
            self.field_names.min_dv: self._min_dv if self._min_dv != 0 else "",
            self.field_names.max_dv: self._max_dv if self._max_dv != 0 else "",
        }

        if self._model.value != -1:
            payload[self.field_names.model] = [self._model.value]

        self._payload.update(payload)

    def _scrape(self):
        self._logger.debug(
            textwrap.dedent(
                f"""{self.__class__.__name__} started with these params:
                {{
                    Make: {self._make.text},
                    Model: {self._model.text},
                    Model Years: {self._start_model_year.value} - {self._end_model_year.value},
                    Min Delta V: {self._min_dv},
                    Max Delta V: {self._max_dv},
                    Primary Damage: {self._primary_damage.text},
                    Secondary Damage: {self._secondary_damage.text},
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
        if not self.running:
            return

        if not response.content:
            self._logger.error(f"Received empty response from {request.url}.")
            self.failed_cases += 1
            return

        case_json: dict = json.loads(response.content)

        # TODO: Implement more robust checks for matching vehicle numbers

        def make_match(make: str):
            """Check if the make of the scraped vehicle matches the "make" scrape parameter."""
            return fuzz.partial_ratio(make.lower(), self._make.text.lower()) >= 90

        def model_match(model: str):
            """
            Check if the model of the scraped vehicle matches the "model" scrape parameter.
            Make an exception if the model is not specified in the scrape parameters
            """
            return (
                fuzz.partial_ratio(model.lower(), self._model.text.lower()) >= 90
                or self._model.value == -1
            )

        def year_match(year: int):
            """
            Check if the year of the scraped vehicle falls within the range specified in the "model year" scrape parameters.
            """
            return self._start_model_year.value <= year <= self._end_model_year.value

        vehicle_nums = (
            []
        )  # Getting multiple matching vehicles in the same case is seemingly very rare, but possible
        vPICDecodeData: list[dict] = case_json.get("VehvPICDecodeData", [])
        for vehicle in vPICDecodeData:
            # TODO: Implement more robust checks for matching vehicle numbers
            # For example, if the VIN decode failed, we may need to get vehicle
            # info from the MakeDesc, ModelDesc, etc from the "Vehicles" list
            if (
                make_match(vehicle.get("Make", ""))
                and model_match(vehicle.get("Model", ""))
                and year_match(int(vehicle.get("ModelYear", -1)))
            ):
                vehicle_nums.append(vehicle["VEHNO"])

        case_id = case_json.get("CaseId", -1)

        if not vehicle_nums:
            self._logger.warning(f"No matching vehicles found in case {case_id}.")
            self.failed_cases += 1
            return

        self._logger.debug(f"Vehicle numbers: {vehicle_nums}")
        print(vehicle_nums)

        key_events = []
        for event in case_json.get("Events", []):
            primary_veh_num = event["VehNum"]
            alt_veh_num = -1
            alt_veh_desc = event["ObjectContactDesc"]
            if event["ObjectContactClassDesc"] == "Vehicle":
                alt_veh_num = int(alt_veh_desc[-1])

            primary_veh_dmg = event["AreaDamageDesc"]
            alt_veh_dmg = event["VehContactDamageDesc"]

            # JSON does not carry the damage IDs, so we need to match the damage planes
            # The strings may not be exactly the same, so we use fuzzy matching here
            primary_dmg_match = (
                fuzz.partial_ratio(self._primary_damage.text, primary_veh_dmg)
                >= self._fuzz_threshold
            ) or self._primary_damage.value == -1

            contacted_dmg_match = (
                fuzz.partial_ratio(self._primary_damage.text, alt_veh_dmg)
                >= self._fuzz_threshold
            ) or self._primary_damage.value == -1

            # voi = vehicle of interest
            for voi in vehicle_nums:
                formatted_event = {
                    "event_num": event["SeqNum"],
                    "voi": voi,
                    "alt_veh_num": alt_veh_num,
                    "alt_veh_desc": alt_veh_desc,
                }

                if voi != primary_veh_num and voi != alt_veh_num:
                    continue
                elif voi == primary_veh_num and primary_dmg_match:
                    key_events.append(formatted_event)

                # If the vehicle of interest is the alternate vehicle and the damage matches, make it
                # so the alternate vehicle for the voi is the primary vehicle
                elif voi == alt_veh_num and contacted_dmg_match:
                    formatted_event["alt_veh_num"] = primary_veh_num
                    formatted_event["alt_veh_desc"] = "Vehicle #" + str(primary_veh_num)
                    key_events.append(formatted_event)

        self._logger.debug(f"Key events: {key_events}")

        # go through vehicles and add CDCs and crush profiles (if available)
        ext_veh_forms = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for cdc in case_json["CDCs"]:
            veh_num = cdc["VehNum"]
            event_num = cdc["SeqNum"]
            ext_veh_forms[veh_num]["CDCs"][event_num] = cdc

        for crush_profile in case_json["CrushProfiles"]:
            veh_num = crush_profile["VehNum"]
            event_num = crush_profile["SeqNum"]
            ext_veh_forms[veh_num]["CrushProfiles"][event_num] = crush_profile

        failed_events = 0
        for event in key_events:
            self._logger.debug(f"Event: {event}")

            cdc_event = ext_veh_forms[event["voi"]]["CDCs"].get(event["event_num"])
            if not cdc_event:
                self._logger.warning(
                    f"Vehicle {event['voi']} does not have a CDC for event {event['event_num']}."
                )
                failed_events += 1
                continue

            def check_dv(dv: str):
                """Check if the delta-v value is numeric and return it as an int, or None if it isn't."""
                dv = dv.split(" ")[0]
                if dv.lstrip("-").isnumeric():
                    return int(dv)

            total_dv = check_dv(cdc_event["DVTotal"])
            lat_dv = check_dv(cdc_event["DVLat"])
            long_dv = check_dv(cdc_event["DVLong"])

            self._logger.debug(f"Delta-V: {total_dv}, {lat_dv}, {long_dv}")

            # if any of the delta-v values are missing, skip this event
            if any(dv is None for dv in (total_dv, lat_dv, long_dv)):
                self._logger.warning(
                    f"One or more of Delta-V values not found for event {event['event_num']} in case {case_id}."
                )
                failed_events += 1
                continue

        print("NOT IMPLEMENTED YET!")
