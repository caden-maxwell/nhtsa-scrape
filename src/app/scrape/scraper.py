import enum
from io import BytesIO
import json
import logging
import os
from pathlib import Path
import textwrap  # To make multiline strings look nice in the code
import time
import requests

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw

from .request_handler import RequestHandler, Request


class Priority(enum.Enum):
    """Enum for request priorities. Lower integer is higher priority."""

    ALL_COMBOS = 0
    MODEL_COMBO = 1
    IMAGE = 1
    CASE = 2
    CASE_LIST = 3


class ScrapeEngine(QObject):
    event_parsed = pyqtSignal(dict)
    started = pyqtSignal()
    completed = pyqtSignal()  # Used to signal that the scrape is *complete*
    finished = pyqtSignal()  # Used to signal that the scrape has *stopped*

    def __init__(self, search_params, image_set, case_limit):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)
        self.CASE_URL = (
            "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
        )
        self.CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

        self.case_limit = case_limit
        self.image_set = image_set

        # Get default search payload and update with user input
        payload_path = Path(__file__).parent / "payload.json"
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

    def stop(self):
        self.running = False
        self.finished.emit()

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
        self.stop()

    def limit_reached(self):
        return self.success_cases >= self.case_limit

    def check_complete(self):
        if (
            not self.req_handler.contains(Priority.CASE.value)
            and not self.req_handler.get_ongoing_requests(Priority.CASE.value)
            and self.final_page
        ):
            self.complete()

    def enqueue_extra_case(self):
        if self.extra_cases:
            caseid = self.extra_cases.pop()
            self.logger.debug(f"Enqueuing extra case: {caseid}")
            self.req_handler.enqueue_request(
                Request(f"{self.CASE_URL}{caseid}", priority=Priority.CASE.value)
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
                Image Set: {self.image_set}
            }}"""
            )
        )
        request = Request(
            self.CASE_LIST_URL,
            method="POST",
            params=self.search_payload,
            priority=Priority.CASE_LIST.value,
        )
        self.req_handler.enqueue_request(request)

    @pyqtSlot(int, str, str, str)
    def handle_response(self, priority, url, response_text, cookie):
        if priority == Priority.CASE_LIST.value:
            self.parse_case_list(url, response_text)
        elif priority == Priority.CASE.value:
            self.parse_case(url, response_text, cookie)
        elif priority == Priority.IMAGE.value:
            self.parse_image(url, response_text, cookie)
        else:
            self.logger.error(
                f"Scrape engine received response with invalid priority: {priority}."
            )

    def parse_case_list(self, url, response_text):
        if not self.running:
            return

        if not response_text:
            self.logger.error(f"Received empty response from {url}.")
            self.final_page = True
            return

        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.complete()
            return

        soup = BeautifulSoup(response_text, "html.parser")
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
                Request(f"{self.CASE_URL}{case_id}", priority=Priority.CASE.value)
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
            Request(
                self.CASE_LIST_URL,
                method="POST",
                params=self.search_payload,
                priority=Priority.CASE_LIST.value,
            )
        )

    def parse_case(self, url, response_text, cookie):
        if not self.running:
            return

        if not response_text:
            self.logger.error(f"Received empty response from {url}.")
            self.enqueue_extra_case()
            self.failed_cases += 1
            return

        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.complete()
            return

        case_xml = BeautifulSoup(response_text, "xml")

        case_id = case_xml.find("CaseForm").get("caseID")
        summary = case_xml.find("Summary").text
        # print("\n=========================================")
        # print(f"Case ID: {caseid}")
        # print(f"Summary: {summary}")

        make = int(self.search_payload["ddlMake"])
        model = int(self.search_payload["ddlModel"])
        start_year = int(self.search_payload["ddlStartModelYear"])
        end_year = (
            9999
            if (year := int(self.search_payload["ddlEndModelYear"])) == -1
            else year
        )

        make_match = (
            lambda veh_sum: make == int(veh_sum.find("Make").get("value")) or make == -1
        )
        model_match = (
            lambda veh_sum: model == int(veh_sum.find("Model").get("value"))
            or model == -1
        )
        year_match = (
            lambda veh_sum: start_year <= int(veh_sum.find("Year").text) <= end_year
        )

        vehicle_nums = [
            int(veh_summary.get("VehicleNumber"))
            for veh_summary in case_xml.find_all("VehicleSum")
            if make_match(veh_summary)
            and model_match(veh_summary)
            and year_match(veh_summary)
        ]

        if not vehicle_nums:
            self.logger.warning(f"No matching vehicles found in case {case_id}.")
            self.enqueue_extra_case()
            self.failed_cases += 1
            return
        # print(f"Vehicle numbers: {vehicle_nums}")

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
        # print(f"Key events: {key_events}")

        veh_ext_forms = case_xml.find("VehicleExteriorForms")
        gen_veh_forms = case_xml.find("GeneralVehicleForms")

        failed_events = 0
        for event in key_events:
            # print(f"Event: {event}")

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
            tot = None
            lat = None
            lon = None
            if cdc_event:
                tot = int(cdc_event.find("Total")["value"])
                lat = int(cdc_event.find("Lateral")["value"])
                lon = int(cdc_event.find("Longitudinal")["value"])
                # print(f"Total: {tot}, Longitudinal: {lon}, Lateral: {lat}")
            else:
                self.logger.warning(
                    f"No CDCevent found for event {event['en']} in case {case_id}."
                )

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
            final_crush = []
            if avg_c1 >= 0:
                final_crush = [
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
            data = {
                "summary": summary,
                "case_id": case_id,
                "event_num": event["en"],
                "case_num": case_xml.find("Case")["CaseStr"],
                "veh_num": veh_ext_form["VehicleNumber"],
                "make": veh_ext_form.find("Make").text,
                "model": veh_ext_form.find("Model").text,
                "model_year": veh_ext_form.find("ModelYear").text,
                "curb_weight": float(veh_ext_form.find("CurbWeight").text),
                "dmg_loc": veh_ext_form.find("DeformationLocation").text,
                "underride": veh_ext_form.find("OverUnderride").text,
                "edr": veh_ext_form.find("EDR").text,
                "total_dv": float(tot),
                "long_dv": float(lon),
                "lat_dv": float(lat),
                "smashl": float(smash_l),
                "crush": final_crush,
            }

            # Alternate Vehicle Info
            data["a_veh_num"] = event["an"]
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
                alt_temp = {
                    "a_make": alt_ext_form.find("Make").text,
                    "a_model": alt_ext_form.find("Model").text,
                    "a_year": alt_ext_form.find("ModelYear").text,
                    "a_curb_weight": float(curbweight)
                    if (curbweight := alt_ext_form.find("CurbWeight").text).isnumeric()
                    else data["curb_weight"],
                    "a_dmg_loc": damloc.text
                    if (damloc := alt_ext_form.find("DeformationLocation"))
                    else "--",
                }
            else:
                alt_temp = {
                    "a_year": "--",
                    "a_make": "--",
                    "a_model": "--",
                    "a_curb_weight": 99999.0,
                    "a_dmg_loc": "--",
                }
            data.update(alt_temp)
            self.total_events += 1
            self.event_parsed.emit(data)

        if failed_events >= len(key_events):
            self.logger.warning(
                f"Insufficient data for caseID {case_id}. Excluding from results."
            )
            self.enqueue_extra_case()
            self.failed_cases += 1
            return

        self.success_cases += 1

    def parse_image(self, url, response_text, cookie):
        return
        img_form = case_xml.find("IMGForm")
        if not img_form:
            print("No ImgForm found.")
            return

        veh_img_areas = {
            "F": "Front",
            "B": "Back",
            "L": "Left",
            "R": "Right",
            "FL": "Frontleftoblique",
            "FR": "Backleftoblique",
            "BL": "Frontrightoblique",
            "BR": "Backrightoblique",
        }

        img_set_lookup = {}
        for k, v in veh_img_areas.items():
            img_set_lookup[k] = [
                (img.text, img["version"])
                for img in img_form.find("Vehicle", {"VehicleNumber": event["voi"]})
                .find(v)
                .find_all("image")
            ]

        image_set = image_set.split(" ")[0]
        img_elements = img_set_lookup.get(image_set, [])

        if not img_elements:
            print(
                f"No images found for image set {image_set}. Attempting to set to defaults..."
            )
            veh_dmg_areas = {
                2: img_set_lookup["F"],
                5: img_set_lookup["B"],
                4: img_set_lookup["L"],
                3: img_set_lookup["R"],
            }
            img_elements = veh_dmg_areas.get(int(payload["ddlPrimaryDamage"]), [])

        fileName = "i"
        while True:
            for img_element in img_elements:
                img_url = (
                    "https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID="
                    + str(img_element[0])
                    + "&CaseID="
                    + caseid
                    + "&Version="
                    + str(img_element[1])
                )
                print(f"Image URL: {img_url}")

                cookie = {"Cookie": response.headers["Set-Cookie"]}
                response = requests.get(img_url, headers=cookie)
                img = Image.open(BytesIO(response.content))
                draw = ImageDraw.Draw(img)
                draw.rectangle(((0, 0), (300, 30)), fill="white")
                tot_mph = str(float(tot) * 0.6214)
                img_text = "Case No: " + caseid + " - NASS DV: " + tot_mph
                draw.text(
                    (0, 0),
                    img_text,
                    (220, 20, 60),
                    font=ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 24),
                )
                img.show()
                g = input(
                    "Select: [NE]xt Image, [SA]ve Image, [DE]lete Case, [FT]ront, [FL]ront Left, [LE]ft,"
                    "[BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right: "
                )

                def check_image_set(image_set):
                    if not self.image_set:
                        self.image_set = img_set_lookup["F"]
                        if "F" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["F"]
                        elif "R" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["R"]
                        elif "B" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["B"]
                        elif "L" in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup["L"]
                        print("Empty Image Set")
                        return self.image_set
                    else:
                        return self.image_set

                if "sa" in g.lower():
                    caseid_path = (
                        os.getcwd()
                        + "/"
                        + self.search_payload["ddlStartModelYear"]
                        + "_"
                        + self.search_payload["ddlEndModelYear"]
                        + "_"
                        + self.search_payload["ddlMake"]
                        + "_"
                        + self.search_payload["ddlModel"]
                        + "_"
                        + self.search_payload["ddlPrimaryDamage"]
                    )
                    if not os.path.exists(caseid_path):
                        os.makedirs(caseid_path)
                    os.chdir(caseid_path)

                    img_num = str(img_element[0])
                    fileName = caseid_path + "//" + img_num + ".jpg"
                    img.save(fileName)
                    g = "de"
                    break
                elif "ne" in g.lower():
                    continue
                elif "de" in g.lower():
                    break
                elif "ft" in g.lower():
                    img_elements = check_image_set(front_images)
                    break
                elif "fr" in g.lower():
                    img_elements = check_image_set(frontright_images)
                    break
                elif "ri" in g.lower():
                    img_elements = check_image_set(right_images)
                    break
                elif "br" in g.lower():
                    img_elements = check_image_set(backright_images)
                    break
                elif "ba" in g.lower():
                    img_elements = check_image_set(back_images)
                    break
                elif "bl" in g.lower():
                    img_elements = check_image_set(backleft_images)
                    break
                elif "le" in g.lower():
                    img_elements = check_image_set(left_images)
                    break
                elif "fl" in g.lower():
                    img_elements = check_image_set(frontleft_images)
                    break
                img.close()
            if "de" in g.lower():
                break

    def get_an(self, voi: int, event: BeautifulSoup, num_vehicles: int):
        # For whatever reason, the area of damage and contacted area of damage values are off by 1 in the XML viewer
        area_of_dmg = int(event.find("AreaOfDamage")["value"]) - 1
        contacted_aod = int(event.find("ContactedAreaOfDamage")["value"]) - 1

        contacted = event.find("Contacted")
        vehicle_number = int(event["VehicleNumber"])

        primary_damage = int(self.search_payload["ddlPrimaryDamage"])
        primary_dmg_match = primary_damage == area_of_dmg or primary_damage == -1
        contacted_dmg_match = primary_damage == contacted_aod or primary_damage == -1

        if (
            voi == vehicle_number and primary_dmg_match
        ):  # If the voi is the primary vehicle, return the contacted vehicle/object as the an
            if int(contacted["value"]) > num_vehicles:
                return contacted.text
            else:
                return int(contacted["value"])
        elif (
            str(voi) in contacted.text and contacted_dmg_match
        ):  # If the voi is the contacted vehicle, return the primary vehicle as the an
            return vehicle_number

        return 0  # voi not involved in this event
