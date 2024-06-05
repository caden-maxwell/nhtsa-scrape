import enum
import json
import logging
from pathlib import Path
import textwrap  # To make multiline strings look nice in the code
import time

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from bs4 import BeautifulSoup
import numpy as np

from . import RequestHandler, RequestQueueItem


class Priority(enum.Enum):
    """Enum for request priorities. Lower integer is higher priority."""

    ALL_COMBOS = 0
    MODEL_COMBO = 1
    IMAGE = 2
    CASE_FOR_IMAGE = 3
    CASE = 4
    CASE_LIST = 5


class ScrapeEngine(QObject):
    event_parsed = pyqtSignal(dict, bytes, str)
    started = pyqtSignal()
    completed = pyqtSignal()
    CASE_URL = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
    CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

    def __init__(self, search_params, case_limit):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)
        self.case_limit = case_limit

        # Get default search payload and update with user input
        payload_path = Path(__file__).parent.parent / "resources" / "payload.json"
        self.search_payload = {}
        with open(payload_path, "r") as f:
            self.search_payload = dict(json.load(f))
        self.search_payload.update(search_params)

        self.running = False
        self.start_time = 0

        self.current_page = 1
        self.final_page = False
        self.extra_cases = []
        self.success_cases = 0
        self.failed_cases = 0
        self.total_events = 0

    def start(self):
        self.running = True
        self.started.emit()
        self.scrape()

    def complete(self):
        # Order matters here, otherwise the request handler will start making
        # unnecessary case list requests once the individual cases are cleared
        self.req_handler.clear_queue(Priority.CASE_LIST.value)
        self.req_handler.clear_queue(Priority.CASE.value)

        if self.success_cases + self.failed_cases < 1:
            self.logger.info("No data was found. Scrape complete.")
        else:
            total_cases = self.success_cases + self.failed_cases
            self.logger.info(
                textwrap.dedent(
                    f"""
                ---- Scrape Summary ----
                - Total Cases Requested: {total_cases}
                    - Successfully Parsed: {self.success_cases} ({self.success_cases / (total_cases) * 100:.2f}%)
                    - Failed to Parse: {self.failed_cases} ({self.failed_cases / (total_cases) * 100:.2f}%)
                - Total Events Extracted: {self.total_events}
                - Time Elapsed: {time.time() - self.start_time:.2f}s
                -------------------------"""
                )
            )
        self.completed.emit()
        self.running = False

    def limit_reached(self):
        return self.success_cases >= self.case_limit

    def check_complete(self):
        if (
            not self.req_handler.contains(Priority.CASE.value)
            and self.final_page
            and self.running
        ):
            self.complete()

    def enqueue_extra_case(self):
        if self.extra_cases:
            caseid = self.extra_cases.pop()
            self.logger.debug(f"Enqueuing extra case: {caseid}")
            self.req_handler.enqueue_request(
                RequestQueueItem(
                    f"{self.CASE_URL}{caseid}&docinfo=0", priority=Priority.CASE.value
                )
            )

    def scrape(self):
        self.start_time = time.time()
        self.logger.debug(
            textwrap.dedent(
                f"""Scrape engine started with these params:
            {{
                Make: {self.search_payload['ddlMake']},
                Model: {self.search_payload['ddlModel']},
                Model Start Year: {self.search_payload['ddlStartModelYear']},
                Model End Year: {self.search_payload['ddlEndModelYear']},
                Min Delta V: {self.search_payload['tDeltaVFrom']},
                Max Delta V: {self.search_payload['tDeltaVTo']},
                Primary Damage: {self.search_payload['ddlPrimaryDamage']},
                Secondary Damage: {self.search_payload['lSecondaryDamage']},
                Case Limit: {self.case_limit},
            }}"""
            )
        )
        request = RequestQueueItem(
            self.CASE_LIST_URL,
            method="POST",
            params=self.search_payload,
            priority=Priority.CASE_LIST.value,
        )
        self.req_handler.enqueue_request(request)

    @pyqtSlot(int, str, bytes, str, dict)
    def handle_response(self, priority, url, response_content, cookie, extra_data):
        if priority == Priority.CASE_LIST.value:
            self.parse_case_list(url, response_content)
        elif priority == Priority.CASE.value:
            self.parse_case(url, response_content, cookie)
        else:
            self.logger.error(
                f"Scrape engine received response with invalid priority: {priority}."
            )

    def parse_case_list(self, url, response_content):
        if not self.running:
            return

        if not response_content:
            self.logger.error(f"Received empty response from {url}.")
            self.final_page = True
            return

        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.complete()
            return

        soup = BeautifulSoup(response_content, "html.parser")
        page_dropdown = soup.find("select", id="ddlPage")
        if not page_dropdown:
            self.logger.warning(
                f"No cases found on page {self.search_payload['currentPage']}."
            )
            self.final_page = True
            return

        # Get all caseIDs on the current page
        case_ids = []
        tables = soup.find_all("table")
        if len(tables) > 1:
            table = tables[1]  # The second table should have all the case links
            case_urls = [a["href"] for a in table.find_all("a")]
            case_ids = [url.split("=")[2] for url in case_urls]
        else:
            self.logger.warning(
                f"No cases found on page {self.search_payload['currentPage']}."
            )
            self.final_page = True
            return

        # Number of needed cases is the case limit minus the number of cases already parsed.
        # Anything extra will be set aside to parse later if there are any failures
        self.extra_cases = case_ids[self.case_limit - self.success_cases :]
        case_ids = case_ids[: self.case_limit - self.success_cases]
        self.logger.info(
            f"Requesting {len(case_ids)} case{'s'[:len(case_ids)^1]} from page {self.current_page}..."
        )
        for case_id in case_ids:
            self.req_handler.enqueue_request(
                RequestQueueItem(
                    f"{self.CASE_URL}{case_id}&docinfo=0", priority=Priority.CASE.value
                )
            )

        total_pages = int(page_dropdown.find_all("option")[-1].text)
        if self.current_page == total_pages:
            self.logger.debug("Last page reached.")
            self.final_page = True
            return

        self.current_page += 1
        self.search_payload["currentPage"] = self.current_page
        self.logger.debug(f"Queueing page {self.current_page}...")

        self.req_handler.enqueue_request(
            RequestQueueItem(
                self.CASE_LIST_URL,
                method="POST",
                params=self.search_payload,
                priority=Priority.CASE_LIST.value,
            )
        )

    def parse_case(self, url, response_content, cookie):
        if not self.running:
            return

        if not response_content:
            self.logger.error(f"Received empty response from {url}.")
            self.enqueue_extra_case()
            self.failed_cases += 1
            return

        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.complete()
            return

        case_xml = BeautifulSoup(response_content, "xml")

        case_id = case_xml.find("CaseForm").get("caseID")
        summary = case_xml.find("Summary").text
        # print("\n=========================================")
        # print(f"Case ID: {caseid}")
        # print(f"Summary: {summary}")

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
            self.enqueue_extra_case()
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
                an := self.get_an(voi, event, veh_amount)
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
                # self.logger.debug(f"Total: {total_dv}, Longitudinal: {long_dv}, Lateral: {lat_dv}")
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
            # print(f"Crush: {final_crush}, Smash: {smash_l}")

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
                    "a_curb_weight": float(curb_weight)
                    if (curb_weight := alt_ext_form.find("CurbWeight").text).isnumeric()
                    else event_data["curb_weight"],
                    "a_dmg_loc": dmg_loc.text
                    if (dmg_loc := alt_ext_form.find("DeformationLocation"))
                    else "--",
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

            # Restitution Calculation
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
            self.event_parsed.emit(event_data, response_content, cookie)

        if failed_events >= len(key_events):
            self.logger.warning(
                f"Insufficient data for caseID {case_id}. Excluding from results."
            )
            self.enqueue_extra_case()
            self.failed_cases += 1
            return

        self.success_cases += 1

    def get_an(self, voi: int, event: BeautifulSoup, num_vehicles: int):
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
