import textwrap
from time import time
from bs4 import BeautifulSoup
import numpy as np
from requests import Response

from PyQt6.QtCore import QThread

from app.scrape import RequestQueueItem, BaseScraper, Priority
from app.resources import payload_NASS


class ScraperNASS(BaseScraper):
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

    def __init__(self, search_params):
        super().__init__()

        self.search_payload = payload_NASS
        self.search_payload.update(search_params)

    def _scrape(self):
        self.start_time = time()
        self.logger.debug(
            textwrap.dedent(
                f"""NASS Scrape Engine started with these params:
                {{
                    Make: {self.search_payload['ddlMake']},
                    Model: {self.search_payload['ddlModel']},
                    Model Start Year: {self.search_payload['ddlStartModelYear']},
                    Model End Year: {self.search_payload['ddlEndModelYear']},
                    Min Delta V: {self.search_payload['tDeltaVFrom']},
                    Max Delta V: {self.search_payload['tDeltaVTo']},
                    Primary Damage: {self.search_payload['ddlPrimaryDamage']},
                    Secondary Damage: {self.search_payload['lSecondaryDamage']},
                }}"""
            )
        )
        request = RequestQueueItem(
            self.CASE_LIST_URL,
            method="GET",
            params=self.search_payload,
            priority=Priority.CASE_LIST.value,
            callback=self._parse_case_list,
        )
        self.req_handler.enqueue_request(request)

    def _parse_case_list(self, request: RequestQueueItem, response: Response):
        if not self.running:
            return

        if not response.content:
            self.logger.error(
                f"Received empty response from {request.url}. Ending scrape..."
            )
            self.complete()
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Get all caseIDs on the current page
        case_ids = []
        tables = soup.find_all("table")
        if len(tables) > 1:
            table = tables[1]  # The second table should have all the case links
            case_urls = [a["href"] for a in table.find_all("a")]
            case_ids = [url.split("=")[2] for url in case_urls]

        if not case_ids:
            self.logger.debug(
                f"No cases found on page {self.search_payload['currentPage']}. Scrape complete."
            )
            self.complete()
            return

        self.logger.info(
            f"Requesting {len(case_ids)} case{'s'[:len(case_ids)^1]} from page {self.current_page}..."
        )
        for case_id in case_ids:
            self.req_handler.enqueue_request(
                RequestQueueItem(
                    f"{self.CASE_URL}{case_id}&docinfo=0",
                    priority=Priority.CASE.value,
                    callback=self.__parse_case,
                )
            )

        self.current_page += 1
        self.search_payload["currentPage"] = self.current_page
        self.logger.debug(f"Queueing page {self.current_page}...")

        self.req_handler.enqueue_request(
            RequestQueueItem(
                self.CASE_LIST_URL,
                method="POST",
                params=self.search_payload,
                priority=Priority.CASE_LIST.value,
                callback=self._parse_case_list,
            )
        )

    def __parse_case(self, request: RequestQueueItem, response: Response):
        if not self.running:
            return

        if not response.content:
            self.logger.error(f"Received empty response from {request.url}.")
            self.failed_cases += 1
            return

        case_xml = BeautifulSoup(response.content, "xml")

        case_id = case_xml.find("CaseForm").get("caseID")
        summary = case_xml.find("Summary").text

        make = int(self.search_payload["ddlMake"])
        model = int(self.search_payload["ddlModel"])
        start_year = int(self.search_payload["ddlStartModelYear"])
        end_year = (
            year
            if (year := int(self.search_payload["ddlEndModelYear"])) != -1
            else 9999
        )

        def make_match(veh_sum):
            return make == int(veh_sum.find("Make").get("value")) or make == -1

        def model_match(veh_sum):
            return model == int(veh_sum.find("Model").get("value")) or model == -1

        def year_match(veh_sum: BeautifulSoup, start_year, end_year):
            year = veh_sum.find("Year").text
            if year == "Unknown":
                if start_year == -1 and end_year == 9999:
                    return True
                return False
            elif not year.isnumeric():
                return False
            return start_year <= int(year) <= end_year

        vehicle_nums = [
            int(veh_summary.get("VehicleNumber"))
            for veh_summary in case_xml.find_all("VehicleSum")
            if make_match(veh_summary)
            and model_match(veh_summary)
            and year_match(veh_summary, start_year, end_year)
        ]

        if not vehicle_nums:
            self.logger.warning(f"No matching vehicles found in case {case_id}.")
            self.failed_cases += 1
            return
        self.logger.debug(f"Vehicle numbers: {vehicle_nums}")

        veh_amount = int(case_xml.find("NumberVehicles").text)
        key_events = [
            {
                "en": int(event["EventNumber"]),
                "voi": voi,
                "an": an,
            }
            for voi in vehicle_nums
            for event in case_xml.find_all("EventSum")
            if (
                an := self.__get_an(voi, event, veh_amount)
            )  # Add event to key_events only if 'an' is truthy.
        ]
        self.logger.debug(f"Key events: {key_events}")

        veh_ext_forms = case_xml.find("VehicleExteriorForms")
        gen_veh_forms = case_xml.find("GeneralVehicleForms")

        failed_events = 0
        for event in key_events:
            self.logger.debug(f"Event: {event}")

            veh_ext_form = veh_ext_forms.find(
                "VehicleExteriorForm", {"VehicleNumber": event["voi"]}
            )
            if not veh_ext_form:
                self.logger.warning(
                    f"No VehicleExteriorForm found for vehicle {event['voi']} in case {case_id}."
                )
                failed_events += 1
                continue

            cdc_event = veh_ext_form.find("CDCevent", {"eventNumber": event["en"]})
            total_dv = None
            lat_dv = None
            long_dv = None
            if cdc_event:
                total_dv = (
                    int(dv)
                    if (dv := cdc_event.find("Total").text).lstrip("-").isnumeric()
                    else None
                )
                lat_dv = (
                    int(dv)
                    if (dv := cdc_event.find("Lateral").text).lstrip("-").isnumeric()
                    else None
                )
                long_dv = (
                    int(dv)
                    if (dv := cdc_event.find("Longitudinal").text)
                    .lstrip("-")
                    .isnumeric()
                    else None
                )
            else:
                self.logger.warning(
                    f"No CDCevent found for event {event['en']} in case {case_id}."
                )

            if total_dv is None or lat_dv is None or long_dv is None:
                self.logger.warning(
                    f"Delta-V not found for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            crush_object = None
            for obj in veh_ext_form.find_all("CrushObject"):
                if event["en"] == int(obj.find("EventNumber").text):
                    crush_object = obj
                    break

            if not crush_object:
                self.logger.warning(
                    f"No CrushObject found for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            avg_c1 = float(crush_object.find("AVG_C1")["value"])
            smash_l = None
            crush = []
            if avg_c1 >= 0:
                crush = [
                    avg_c1,
                    float(crush_object.find("AVG_C2")["value"]),
                    float(crush_object.find("AVG_C3")["value"]),
                    float(crush_object.find("AVG_C4")["value"]),
                    float(crush_object.find("AVG_C5")["value"]),
                    float(crush_object.find("AVG_C6")["value"]),
                ]
                smash_l = crush_object.find("SMASHL")["value"]
            else:
                self.logger.warning(
                    f"No crush in file for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            # VOI Info
            event_data = {
                "summary": summary,
                "case_id": case_id,
                "event_num": event["en"],
                "case_num": case_xml.find("Case")["CaseStr"],
                "vehicle_num": veh_ext_form["VehicleNumber"],
                "make": veh_ext_form.find("Make").text,
                "model": veh_ext_form.find("Model").text,
                "model_year": veh_ext_form.find("ModelYear").text,
                "curb_weight": float(veh_ext_form.find("CurbWeight").text),
                "dmg_loc": cdc_event.find("DeformationLocation").text,
                "underride": cdc_event.find("OverUnderride").text,
                "edr": veh_ext_form.find("EDR").text,
                "total_dv": float(total_dv),
                "long_dv": float(long_dv),
                "lat_dv": float(lat_dv),
                "smashl": float(smash_l),
                "crush": crush,
            }

            # Alternate Vehicle Info
            event_data["a_veh_num"] = event["an"]
            alt_ext_form = veh_ext_forms.find(
                "VehicleExteriorForm", {"VehicleNumber": event["an"]}
            )
            alt_ext_form = (
                alt_ext_form
                if alt_ext_form
                else gen_veh_forms.find(
                    "GeneralVehicleForm", {"VehicleNumber": event["an"]}
                )
            )

            if alt_ext_form:
                alt_data = {
                    "a_make": alt_ext_form.find("Make").text,
                    "a_model": alt_ext_form.find("Model").text,
                    "a_year": alt_ext_form.find("ModelYear").text,
                    "a_curb_weight": (
                        float(curb_weight)
                        if (
                            curb_weight := alt_ext_form.find("CurbWeight").text
                        ).isnumeric()
                        else event_data["curb_weight"]
                    ),
                    "a_dmg_loc": (
                        dmg_loc.text
                        if (dmg_loc := alt_ext_form.find("DeformationLocation"))
                        else "--"
                    ),
                }
            else:
                alt_data = {
                    "a_year": "--",
                    "a_make": "--",
                    "a_model": "--",
                    "a_curb_weight": 99999.0,
                    "a_dmg_loc": "--",
                }

            # Avg crush (inches)
            c_bar = 0.393701 * ((crush[0] + crush[5]) * 0.5 + sum(crush[1:5])) / 5

            # NASS DV in MPH
            NASS_dv = float(total_dv) * 0.621371

            # Vehicle Weights in LBS
            voi_wt = event_data["curb_weight"] * 2.20462
            a_wt = alt_data["a_curb_weight"] * 2.20462

            NASS_vc = NASS_dv / (a_wt / (voi_wt + a_wt))

            # Restitution Calculation...?
            e = 0.5992 * np.exp(
                -0.1125 * NASS_vc + 0.003889 * NASS_vc**2 - 0.0001153 * NASS_vc**3
            )
            TOT_dv = NASS_dv * (1.0 + e)

            calcs = {
                "c_bar": c_bar,
                "NASS_dv": NASS_dv,
                "NASS_vc": NASS_vc,
                "e": e,
                "TOT_dv": TOT_dv,
            }

            event_data.update(alt_data)
            event_data.update(calcs)

            self.total_events += 1
            self.event_parsed.emit(event_data, response)

        if failed_events >= len(key_events):
            self.logger.warning(
                f"Insufficient data for caseID {case_id}. Excluding from results."
            )
            self.failed_cases += 1
            return

        self.success_cases += 1

    def __get_an(self, voi: int, event: BeautifulSoup, num_vehicles: int):
        # For whatever reason, the area of damage and contacted area of damage values are off by 1 in the XML viewer
        area_of_dmg = int(event.find("AreaOfDamage")["value"]) - 1
        contacted_aod = int(event.find("ContactedAreaOfDamage")["value"]) - 1
        self.logger.debug(f"AODs: {area_of_dmg}, {contacted_aod}")

        contacted = event.find("Contacted")
        vehicle_number = int(event["VehicleNumber"])
        self.logger.debug(f"Nums: {vehicle_number}, {contacted['value']}")

        primary_damage = int(self.search_payload["ddlPrimaryDamage"])
        self.logger.debug(f"Primary Damage: {primary_damage}")

        primary_dmg_match = primary_damage == area_of_dmg or primary_damage == -1
        contacted_dmg_match = primary_damage == contacted_aod or primary_damage == -1
        self.logger.debug(
            f"Matches: primary-{primary_dmg_match}, contacted-{contacted_dmg_match}"
        )

        if (
            voi == vehicle_number and primary_dmg_match
        ):  # If the voi is the primary vehicle, return the contacted vehicle/object as the an
            if int(contacted["value"]) > num_vehicles:
                return contacted.text
            else:
                return int(contacted["value"])
        elif (
            voi == int(contacted["value"]) and contacted_dmg_match
        ):  # If the voi is the contacted vehicle, return the primary vehicle as the an
            return vehicle_number

        return 0  # voi not involved in this event
