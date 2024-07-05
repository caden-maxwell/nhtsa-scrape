from datetime import datetime
import textwrap
from bs4 import BeautifulSoup
import numpy as np
from requests import Response
import json
from collections import defaultdict, namedtuple
from fuzzywuzzy import fuzz

from app.scrape import BaseScraper, RequestQueueItem, Priority, FieldNames
from app.resources import payload_CISS
from app.models import Event


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

        def make_match(vehicle: dict):
            """Check if the make of the scraped vehicle matches the "make" scrape parameter."""
            make = vehicle.get("VPICMakeDesc", "") or vehicle.get("MakeDesc", "")
            return (
                fuzz.partial_ratio(make.lower(), self._make.text.lower())
                >= self._fuzz_threshold
            )

        def model_match(vehicle: dict):
            """
            Check if the model of the scraped vehicle matches the "model" scrape parameter.
            Make an exception if the model is not specified in the scrape parameters
            """
            model = vehicle.get("VPICModelDesc", "") or vehicle.get("ModelDesc", "")
            return (
                fuzz.partial_ratio(model.lower(), self._model.text.lower())
                >= self._fuzz_threshold
                or self._model.value == -1
            )

        def year_match(vehicle: dict):
            """
            Check if the year of the scraped vehicle falls within the range specified in the "model year" scrape parameters.
            """
            year = int(vehicle.get("ModelYear", -1))
            return self._start_model_year.value <= year <= self._end_model_year.value

        vehicle_nums = (
            []
        )  # Getting multiple matching vehicles in the same case is seemingly very rare, but possible
        vehicles: list[dict] = case_json.get("Vehicles", [])
        for vehicle in vehicles:
            if make_match(vehicle) and model_match(vehicle) and year_match(vehicle):
                vehicle_nums.append(vehicle["VEHNUM"])

        case_id = case_json.get("CaseId", -1)

        if not vehicle_nums:
            self._logger.warning(f"No matching vehicles found in case {case_id}.")
            self.failed_cases += 1
            return

        self._logger.debug(f"Vehicle numbers: {vehicle_nums}")

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
        veh_forms = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for cdc in case_json["CDCs"]:
            veh_num = cdc["VehNum"]
            event_num = cdc["SeqNum"]
            veh_forms[veh_num]["CDCs"][event_num] = cdc

        for crush_profile in case_json["CrushProfiles"]:
            veh_num = crush_profile["VehNum"]
            event_num = crush_profile["SeqNum"]
            veh_forms[veh_num]["CrushProfiles"][event_num] = crush_profile

        for vehicle in case_json["Vehicles"]:
            veh_num = vehicle["VEHNUM"]
            veh_forms[veh_num]["Vehicle"] = vehicle

        def check_dv(dv: str):
            """Check if the delta-v value is numeric and return it as an int, or None if it isn't."""
            dv = dv.split(" ")[0]
            if dv.lstrip("-").isnumeric():
                return int(dv)

        failed_events = 0
        for event in key_events:
            self._logger.debug(f"Event: {event}")

            cdc_event = veh_forms[event["voi"]]["CDCs"].get(event["event_num"])
            if not cdc_event:
                self._logger.warning(
                    f"Vehicle {event['voi']} does not have a CDC for event {event['event_num']}."
                )
                failed_events += 1
                continue

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

            crush_profile = veh_forms[event["voi"]]["CrushProfiles"].get(
                event["event_num"]
            )

            if not crush_profile:
                self._logger.warning(
                    f"No crush profile found for event {event['event_num']} in case {case_id}."
                )
                failed_events += 1
                continue

            avg_c1 = crush_profile["AvgC1"]
            if avg_c1.lstrip("-").isnumeric():
                crush = [  # in cm
                    int(avg_c1),
                    int(crush_profile["AvgC2"]),
                    int(crush_profile["AvgC3"]),
                    int(crush_profile["AvgC4"]),
                    int(crush_profile["AvgC5"]),
                    int(crush_profile["AvgC6"]),
                ]
                smashl = crush_profile["SmashL"]  # in cm
                if smashl.split(" ")[0].isnumeric():
                    smashl = int(smashl.split(" ")[0])
            else:
                self._logger.warning(
                    f" No crush in file for event {event['event_num']} in case {case_id}."
                )
                failed_events += 1
                continue

            CM_TO_IN = 0.393701
            KMPH_TO_MPH = 0.621371
            KG_TO_LBS = 2.20462

            voi_curb_wgt = int(
                veh_forms[event["voi"]]["Vehicle"]["CurbWt"].split(" ")[0]
            )  # in kgs
            if alt_veh := veh_forms[event["alt_veh_num"]]["Vehicle"]:
                a_curb_wgt = alt_veh["CurbWt"]
                if a_curb_wgt.isnumeric():
                    a_curb_wgt = int(a_curb_wgt)
                else:
                    a_curb_wgt = voi_curb_wgt
                a_curb_wgt *= KG_TO_LBS  # in lbs

                alt_data = {
                    "a_make": alt_veh["MakeDesc"],
                    "a_model": alt_veh["ModelDesc"],
                    "a_year": alt_veh["ModelYear"],
                    "a_curb_wgt": a_curb_wgt,
                    "a_dmg_loc": alt_veh["DamagePlaneDesc"],
                }
            else:
                alt_data = {
                    "a_make": "--",
                    "a_model": "--",
                    "a_year": "--",
                    "a_curb_wgt": 99999.0,
                    "a_dmg_loc": "--",
                }

            c_bar = CM_TO_IN * ((crush[0] + crush[5]) * 0.5 + sum(crush[1:5])) / 5

            NASS_dv = total_dv * KMPH_TO_MPH

            voi_curb_wgt = voi_curb_wgt * KG_TO_LBS
            a_curb_wgt = alt_data["a_curb_wgt"]
            NASS_vc = NASS_dv / (a_curb_wgt / (voi_curb_wgt + a_curb_wgt))

            # 0.5992 * e^( -0.1125 * NASS_vc + 0.003889 * NASS_vc^2 - 0.0001153 * NASS_vc^3 )
            e = 0.5992 * np.exp(
                -0.1125 * NASS_vc + 0.003889 * NASS_vc**2 - 0.0001153 * NASS_vc**3
            )
            TOT_dv = NASS_dv * (1.0 + e)

            vehicle
            voi_form = veh_forms[event["voi"]]["Vehicle"]
            self.event_parsed.emit(
                Event(
                    summary=case_json["Summary"],
                    scraper_type="CISS",
                    case_num=case_json["CaseNum"],
                    case_id=case_id,
                    vehicle_num=event["voi"],
                    event_num=event["event_num"],
                    make=voi_form["VPICMakeDesc"] or voi_form["MakeDesc"],
                    model=voi_form["VPICModelDesc"] or voi_form["ModelDesc"],
                    model_year=voi_form["ModelYear"],
                    curb_wgt=round(voi_curb_wgt, 2),
                    dmg_loc=cdc_event["AreaDamageDesc"],
                    underride=cdc_event["OverUnderDesc"],
                    edr=voi_form["EDRReadDesc"],
                    total_dv=total_dv,
                    long_dv=long_dv,
                    lat_dv=lat_dv,
                    smashl=smashl,
                    crush1=crush[0],
                    crush2=crush[1],
                    crush3=crush[2],
                    crush4=crush[3],
                    crush5=crush[4],
                    crush6=crush[5],
                    a_veh_num=event["alt_veh_num"],
                    a_veh_desc=event["alt_veh_desc"],
                    a_make=alt_data["a_make"],
                    a_model=alt_data["a_model"],
                    a_year=alt_data["a_year"],
                    a_curb_wgt=round(alt_data["a_curb_wgt"], 2),
                    a_dmg_loc=alt_data["a_dmg_loc"],
                    c_bar=round(c_bar, 6),
                    NASS_dv=round(NASS_dv, 6),
                    NASS_vc=round(NASS_vc, 6),
                    e=round(e, 6),
                    TOT_dv=round(TOT_dv, 6),
                ),
                response,
            )
            self.total_events += 1

        if failed_events >= len(key_events):
            self._logger.warning(
                f"Insufficient data for caseID {case_id}. Excluding from results."
            )
            self.failed_cases += 1
            return

        self.success_cases += 1
