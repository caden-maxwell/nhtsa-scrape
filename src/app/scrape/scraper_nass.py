import textwrap
from bs4 import BeautifulSoup
import numpy as np
from requests import Response

from PyQt6.QtCore import pyqtSlot

from app.scrape import RequestQueueItem, BaseScraper, Priority, FieldNames
from app.resources import payload_NASS
from app.models import Event


class ScraperNASS(BaseScraper):

    search_url = "/LegacyCDS/Search"
    models_url = "/LegacyCDS/GetVehicleModels/"
    case_url = "/nass-cds/CaseForm.aspx?xsl=main.xsl&CaseID={case_id}"
    case_url_raw = (
        "/nass-cds/CaseForm.aspx?GetXML&caseid={case_id}&year=&transform=0&docinfo=0"
    )
    case_list_url = "/LegacyCDS"
    img_url = "/nass-cds/GetBinary.aspx?Image&ImageID={img_id}&CaseID={case_id}&Version={version}"

    # NASS-specific dropdown field ids
    field_names = FieldNames(
        make="ddlMake",
        model="ddlModel",
        start_model_year="ddlStartModelYear",
        end_model_year="ddlEndModelYear",
        primary_damage="ddlPrimaryDamage",
        secondary_damage="lSecondaryDamage",
        min_dv="tDeltaVFrom",
        max_dv="tDeltaVTo",
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

        self._payload = payload_NASS.copy()

        _, self._make = make
        _, self._model = model
        _, self._start_model_year = start_model_year
        _, self._end_model_year = end_model_year
        _, self._primary_damage = primary_damage
        _, self._secondary_damage = secondary_damage
        self._min_dv = min_dv
        self._max_dv = max_dv

        payload = {
            self.field_names.make: self._make,
            self.field_names.model: self._model,
            self.field_names.start_model_year: self._start_model_year,
            self.field_names.end_model_year: self._end_model_year,
            self.field_names.primary_damage: self._primary_damage,
            self.field_names.secondary_damage: (
                self._secondary_damage if self._secondary_damage != -1 else None
            ),
            self.field_names.min_dv: self._min_dv,
            self.field_names.max_dv: self._max_dv,
        }

        self._payload.update(payload)

    def _scrape(self):
        self._logger.debug(
            textwrap.dedent(
                f"""{self.__class__.__name__} started with these params:
                {{
                    Make: {self._payload[self.field_names.make]},
                    Model: {self._payload[self.field_names.model]},
                    Model Start Year: {self._payload[self.field_names.start_model_year]},
                    Model End Year: {self._payload[self.field_names.end_model_year]},
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
                params=self._payload,
                priority=Priority.CASE_LIST.value,
                callback=self._parse_case_list,
                extra_data={"database": "NASS"},
            )
        )

    @pyqtSlot(RequestQueueItem, Response)
    def _handle_response(self, request: RequestQueueItem, response: Response):
        if (
            request.priority == Priority.CASE_LIST.value
            or request.priority == Priority.CASE.value
        ) and request.extra_data.get("database") == "NASS":
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

        # Get all caseIDs on the current page
        table = soup.find(
            "table",
            {"class": "display table table-condensed table-striped table-hover"},
        )
        case_ids = []
        if table:
            urls = [a["href"] for a in table.find_all("a")]
            case_ids = [url.split("=")[-1] for url in urls]

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
                    callback=self._parse_case,
                    extra_data={"database": "NASS"},
                )
            )

        self.current_page += 1
        self._payload["currentPage"] = self.current_page
        self._logger.debug(f"Queueing page {self.current_page}...")

        self._req_case_list()

    def _parse_case(self, request: RequestQueueItem, response: Response):
        if not self.running:
            return

        if not response.content:
            self._logger.error(f"Received empty response from {request.url}.")
            self.failed_cases += 1
            return

        case_xml = BeautifulSoup(response.content, "xml")
        case_id = case_xml.find("CaseForm").get("caseID")

        def make_match(veh_sum: BeautifulSoup):
            return (
                self._make == int(veh_sum.find("Make").get("value")) or self._make == -1
            )

        def model_match(veh_sum: BeautifulSoup):
            return (
                self._model == int(veh_sum.find("Model").get("value"))
                or self._model == -1
            )

        def year_match(veh_sum: BeautifulSoup):
            end_year = self._end_model_year if (self._end_model_year) != -1 else 9999
            year = veh_sum.find("Year").text
            if year == "Unknown":
                if self._start_model_year == -1 and end_year == 9999:
                    return True
                return False
            elif not year.isnumeric():
                return False
            return self._start_model_year <= int(year) <= end_year

        # Get the vehicles in the case that match the search criteria
        vehicle_nums = []
        for veh_summary in case_xml.find_all("VehicleSum"):
            if (
                make_match(veh_summary)
                and model_match(veh_summary)
                and year_match(veh_summary)
            ):
                vehicle_nums.append(int(veh_summary.get("VehicleNumber")))

        if not vehicle_nums:
            self._logger.warning(f"No matching vehicles found in case {case_id}.")
            self.failed_cases += 1
            return
        self._logger.debug(f"Vehicle numbers: {vehicle_nums}")

        veh_amount = int(case_xml.find("NumberVehicles").text)

        key_events = []
        for voi in vehicle_nums:
            for event in case_xml.find_all("EventSum"):
                if an := self.__get_an(voi, event, veh_amount):
                    key_events.append(
                        {
                            "en": int(event["EventNumber"]),
                            "voi": voi,
                            "an": an,  # Alternate vehicle num
                        }
                    )
        self._logger.debug(f"Key events: {key_events}")

        veh_ext_forms = case_xml.find("VehicleExteriorForms")
        gen_veh_forms = case_xml.find("GeneralVehicleForms")

        failed_events = 0
        for event in key_events:
            self._logger.debug(f"Event: {event}")

            veh_ext_form = veh_ext_forms.find(
                "VehicleExteriorForm", {"VehicleNumber": event["voi"]}
            )
            if not veh_ext_form:
                self._logger.warning(
                    f"Vehicle {event['voi']} does not have an exterior vehicle form."
                )
                failed_events += 1
                continue

            cdc_event = veh_ext_form.find("CDCevent", {"eventNumber": event["en"]})
            if not cdc_event:
                self._logger.warning(
                    f"No CDCevent found for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            def check_dv(dv: str):
                """Check if the delta-v value is numeric and return it as an int, or None if it isn't."""
                if dv.lstrip("-").isnumeric():
                    return int(dv)

            total_dv = check_dv(cdc_event.find("Total").text)
            lat_dv = check_dv(cdc_event.find("Lateral").text)
            long_dv = check_dv(cdc_event.find("Longitudinal").text)

            self._logger.debug(f"Delta-V: {total_dv}, {lat_dv}, {long_dv}")

            if total_dv is None or lat_dv is None or long_dv is None:
                self._logger.warning(
                    f"Delta-V not found for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            crush_object = None
            for obj in veh_ext_form.find_all("CrushObject"):
                obj: BeautifulSoup
                if event["en"] == int(obj.find("EventNumber").text):
                    crush_object = obj
                    break

            if not crush_object:
                self._logger.warning(
                    f"No CrushObject found for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            avg_c1 = float(crush_object.find("AVG_C1")["value"])
            smashl = None
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
                smashl = crush_object.find("SMASHL")["value"]
            else:
                self._logger.warning(
                    f"No crush in file for event {event['en']} in case {case_id}."
                )
                failed_events += 1
                continue

            # Alternate Vehicle Info
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

            voi_curb_weight = float(veh_ext_form.find("CurbWeight").text)
            if alt_ext_form:
                alt_data = {
                    "a_make": alt_ext_form.find("Make").text,
                    "a_model": alt_ext_form.find("Model").text,
                    "a_year": alt_ext_form.find("ModelYear").text,
                    "a_curb_weight": (
                        float(voi_curb_weight)
                        if (
                            voi_curb_weight := alt_ext_form.find("CurbWeight").text
                        ).isnumeric()
                        else voi_curb_weight
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
            voi_wt = float(voi_curb_weight) * 2.20462
            a_wt = alt_data["a_curb_weight"] * 2.20462

            NASS_vc = NASS_dv / (a_wt / (voi_wt + a_wt))

            # Restitution...?
            e = 0.5992 * np.exp(
                -0.1125 * NASS_vc + 0.003889 * NASS_vc**2 - 0.0001153 * NASS_vc**3
            )
            TOT_dv = NASS_dv * (1.0 + e)

            self.event_parsed.emit(
                Event(
                    summary=case_xml.find("Summary").text,
                    scraper_type="NASS",
                    case_num=case_xml.find("Case")["CaseStr"],
                    case_id=case_id,
                    vehicle_num=veh_ext_form["VehicleNumber"],
                    event_num=event["en"],
                    make=veh_ext_form.find("Make").text,
                    model=veh_ext_form.find("Model").text,
                    model_year=veh_ext_form.find("ModelYear").text,
                    curb_weight=float(veh_ext_form.find("CurbWeight").text),
                    dmg_loc=cdc_event.find("DeformationLocation").text,
                    underride=cdc_event.find("OverUnderride").text,
                    edr=veh_ext_form.find("EDR").text,
                    total_dv=total_dv,
                    long_dv=long_dv,
                    lat_dv=lat_dv,
                    smashl=float(smashl),
                    crush1=crush[0],
                    crush2=crush[1],
                    crush3=crush[2],
                    crush4=crush[3],
                    crush5=crush[4],
                    crush6=crush[5],
                    a_veh_num=event["an"],
                    a_veh_desc="",  # TODO: Implement this
                    a_make=alt_data["a_make"],
                    a_model=alt_data["a_model"],
                    a_year=alt_data["a_year"],
                    a_curb_weight=alt_data["a_curb_weight"],
                    a_dmg_loc=alt_data["a_dmg_loc"],
                    c_bar=c_bar,
                    NASS_dv=NASS_dv,
                    NASS_vc=NASS_vc,
                    e=e,
                    TOT_dv=TOT_dv,
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

    def __get_an(self, voi: int, event: BeautifulSoup, num_vehicles: int):
        # For whatever reason, the area of damage and contacted area of damage values are off by 1 in the XML viewer
        area_of_dmg = int(event.find("AreaOfDamage")["value"]) - 1
        contacted_aod = int(event.find("ContactedAreaOfDamage")["value"]) - 1
        self._logger.debug(f"AODs: {area_of_dmg}, {contacted_aod}")

        # contacted.value = contacted vehicle number (int)
        # contacted.text = contacted object description (str)
        primary_veh_num = int(event["VehicleNumber"])
        contacted = event.find("Contacted")
        self._logger.debug(f"Vehicle {primary_veh_num}, Contacted {contacted['value']}")

        primary_damage = int(self._payload["ddlPrimaryDamage"])
        self._logger.debug(f"Primary Damage: {primary_damage}")

        primary_dmg_match = primary_damage == area_of_dmg or primary_damage == -1
        contacted_dmg_match = primary_damage == contacted_aod or primary_damage == -1
        self._logger.debug(
            f"Matches: primary-{primary_dmg_match}, contacted-{contacted_dmg_match}"
        )

        # If the voi is the primary vehicle, return the contacted vehicle/object as the an
        if voi == primary_veh_num and primary_dmg_match:
            if int(contacted["value"]) > num_vehicles:
                return contacted.text
            else:
                return int(contacted["value"])
        # If the voi is the contacted vehicle, return the primary vehicle as the an
        elif voi == int(contacted["value"]) and contacted_dmg_match:
            return primary_veh_num

        return 0  # voi not involved in this event
