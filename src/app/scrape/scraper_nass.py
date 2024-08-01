from collections import namedtuple
import textwrap
from bs4 import BeautifulSoup
import numpy as np
from requests import Response

from PyQt6.QtCore import pyqtSlot

from app.scrape import (
    RequestQueueItem,
    BaseScraper,
    Priority,
    FieldNames,
    RequestHandler,
)
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
    edr_url = "/nass-cds/CaseForm.aspx?ViewPage&xsl=VE.xsl&tab=EDR&form=VehicleExteriorForms&baseNode=&vehnum={veh_num}&occnum=-1&pos={edr_id}&pos2=-1&websrc=true&title=Vehicle%20%20Exterior%20-%20EDR&caseid={case_id}&year=&fullimage=false"

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
        req_handler: RequestHandler,
        make,
        model,
        start_model_year,
        end_model_year,
        primary_damage,
        secondary_damage,
        min_dv,
        max_dv,
    ):
        super().__init__(req_handler)

        self._payload = payload_NASS.copy()

        # Named tuple to store the text and value of a dropdown option, as we may need both
        Option = namedtuple("Param", ["text", "value"])
        self._make = Option(*make)
        self._model = Option(*model)
        self._start_model_year = Option(*start_model_year)
        self._end_model_year = Option(*end_model_year)
        self._primary_damage = Option(*primary_damage)
        self._secondary_damage = Option(*secondary_damage)
        self._min_dv = min_dv
        self._max_dv = max_dv

        payload = {
            self.field_names.make: self._make.value,
            self.field_names.model: self._model.value,
            self.field_names.start_model_year: self._start_model_year.value,
            self.field_names.end_model_year: self._end_model_year.value,
            self.field_names.primary_damage: self._primary_damage.value,
            self.field_names.secondary_damage: (
                self._secondary_damage.value
                if self._secondary_damage.value != -1
                else None
            ),
            self.field_names.min_dv: self._min_dv,
            self.field_names.max_dv: self._max_dv,
        }

        self._payload.update(payload)

    def _scrape(self):
        self._logger.info(
            textwrap.dedent(
                f"""
                --== {self.__class__.__name__} Started ==--
                    Make: {self._make.text}
                    Model: {self._model.text}
                    Model Years: {self._start_model_year.text} - {self._end_model_year.text}
                    Primary Damage: {self._primary_damage.text}
                    Secondary Damage: {self._secondary_damage.text}
                    Min Delta V: {self._min_dv}
                    Max Delta V: {self._max_dv}
                --==--==--==--==--==--==--==--
                """
            )
        )

        self._req_case_list()

    def _req_case_list(self):
        self.enqueue_request.emit(
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
            self._logger.info(
                f"No cases found on page {self._payload['currentPage']}. Scrape complete."
            )
            self.complete()
            return

        self._logger.info(
            f"Requesting {len(case_ids)} case{'s'[:len(case_ids)^1]} from page {self.current_page}..."
        )
        requests = []
        for case_id in case_ids:
            requests.append(
                RequestQueueItem(
                    self.ROOT + self.case_url_raw.format(case_id=case_id),
                    priority=Priority.CASE.value,
                    callback=self._parse_case,
                    extra_data={"database": "NASS"},
                )
            )
        self.batch_enqueue.emit(requests)

        self.current_page += 1
        self._payload["currentPage"] = self.current_page
        self._logger.info(f"Queueing page {self.current_page}...")

        self._req_case_list()

    def _parse_case(self, request: RequestQueueItem, response: Response):
        if not self.running:
            return

        if not response.content:
            self._logger.error(
                f"Received empty response from {request.url}. There may be an issue with the server."
            )
            self.failed_cases += 1
            return

        case_xml = BeautifulSoup(response.content, "xml")
        case_id = case_xml.find("CaseForm").get("caseID")

        def make_match(veh_sum: BeautifulSoup):
            return (
                self._make.value == int(veh_sum.find("Make").get("value"))
                or self._make.value == -1
            )

        def model_match(veh_sum: BeautifulSoup):
            return (
                self._model.value == int(veh_sum.find("Model").get("value"))
                or self._model.value == -1
            )

        def year_match(veh_sum: BeautifulSoup):
            end_year = (
                self._end_model_year.value if (self._end_model_year.value) != -1 else 9999
            )
            year = veh_sum.find("Year").text
            if year == "Unknown":
                if self._start_model_year.value == -1 and end_year == 9999:
                    return True
                return False
            elif not year.isnumeric():
                return False
            return self._start_model_year.value <= int(year) <= end_year

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
            self._logger.warning(
                f"No matching vehicles found in case {case_id}. Excluding from results."
            )
            self.failed_cases += 1
            return
        self._logger.debug(f"Vehicle numbers: {vehicle_nums}")

        veh_amount = int(case_xml.find("NumberVehicles").text)

        key_events = []
        for event in case_xml.find_all("EventSum"):
            event: BeautifulSoup

            primary_veh_num = int(event["VehicleNumber"])
            alt_veh_num = -1
            contacted = event.find("Contacted")
            alt_veh_desc = contacted.text
            if int(contacted["value"]) <= veh_amount:
                alt_veh_num = int(contacted["value"])

            # For whatever reason, the area of damage and contacted area of damage values are off by 1 in the XML viewer
            primary_veh_dmg = int(event.find("AreaOfDamage")["value"]) - 1
            alt_veh_dmg = int(event.find("ContactedAreaOfDamage")["value"]) - 1

            primary_dmg = int(self._payload["ddlPrimaryDamage"])
            primary_dmg_match = primary_dmg == primary_veh_dmg or primary_dmg == -1
            contacted_dmg_match = primary_dmg == alt_veh_dmg or primary_dmg == -1

            for voi in vehicle_nums:
                formatted_event = {
                    "event_num": int(event["EventNumber"]),
                    "voi": voi,
                    "alt_veh_num": alt_veh_num,
                    "alt_veh_desc": alt_veh_desc,
                }

                if voi != primary_veh_num and voi != alt_veh_num:
                    continue
                elif voi == primary_veh_num and primary_dmg_match:
                    key_events.append(formatted_event)

                elif voi == alt_veh_num and contacted_dmg_match:
                    formatted_event["alt_veh_num"] = primary_veh_num
                    formatted_event["alt_veh_desc"] = "Vehicle#" + str(primary_veh_num)
                    key_events.append(formatted_event)

        self._logger.debug(f"Key events: {key_events}")

        veh_ext_forms = case_xml.find("VehicleExteriorForms")
        gen_veh_forms = case_xml.find("GeneralVehicleForms")

        def check_dv(dv: str):
            """Check if the delta-v value is numeric and return it as an int, or None if it isn't."""
            if dv.lstrip("-").isnumeric():
                return int(dv)

        failed_events = 0
        for event in key_events:
            self._logger.debug(f"Event: {event}")

            veh_ext_form = veh_ext_forms.find(
                "VehicleExteriorForm", {"VehicleNumber": event["voi"]}
            )
            if not veh_ext_form:
                self._logger.warning(
                    f"Vehicle {event['voi']} in case {case_id} does not have an exterior vehicle form. Skipping..."
                )
                failed_events += 1
                continue

            cdc_event = veh_ext_form.find(
                "CDCevent", {"eventNumber": event["event_num"]}
            )
            if not cdc_event:
                self._logger.warning(
                    f"No CDCevent found for event {event['event_num']} in case {case_id}. Skipping..."
                )
                failed_events += 1
                continue

            total_dv = check_dv(cdc_event.find("Total").text)
            lat_dv = check_dv(cdc_event.find("Lateral").text)
            long_dv = check_dv(cdc_event.find("Longitudinal").text)

            self._logger.debug(f"Delta-V: {total_dv}, {lat_dv}, {long_dv}")

            if any(dv is None for dv in (total_dv, lat_dv, long_dv)):
                self._logger.warning(
                    f"One or more of Delta-V values not found for event {event['event_num']} in case {case_id}. Skipping..."
                )
                failed_events += 1
                continue

            crush_object = None
            for obj in veh_ext_form.find_all("CrushObject"):
                obj: BeautifulSoup
                if event["event_num"] == int(obj.find("EventNumber").text):
                    crush_object = obj
                    break

            if not crush_object:
                self._logger.warning(
                    f"No crush profile for event {event['event_num']} in case {case_id}. Skipping..."
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
                    f"No crush in file for event {event['event_num']} in case {case_id}. Skipping..."
                )
                failed_events += 1
                continue

            # Alternate Vehicle Info
            alt_ext_form = veh_ext_forms.find(
                "VehicleExteriorForm", {"VehicleNumber": event["alt_veh_num"]}
            )
            alt_ext_form = (
                alt_ext_form
                if alt_ext_form
                else gen_veh_forms.find(
                    "GeneralVehicleForm", {"VehicleNumber": event["alt_veh_num"]}
                )
            )

            CM_TO_IN = 0.393701
            KMPH_TO_MPH = 0.621371
            KG_TO_LBS = 2.20462

            voi_curb_wgt = int(veh_ext_form.find("CurbWeight").text)
            if alt_ext_form:
                a_curb_wgt = alt_ext_form.find("CurbWeight").text
                if a_curb_wgt.isnumeric():
                    a_curb_wgt = int(a_curb_wgt)
                else:
                    a_curb_wgt = voi_curb_wgt
                a_curb_wgt *= KG_TO_LBS  # Convert to lbs

                alt_data = {
                    "a_make": alt_ext_form.find("Make").text,
                    "a_model": alt_ext_form.find("Model").text,
                    "a_year": alt_ext_form.find("ModelYear").text,
                    "a_curb_wgt": a_curb_wgt,
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
                    "a_curb_wgt": 99999.0,
                    "a_dmg_loc": "--",
                }

            # Avg crush (converted to inches)
            c_bar = CM_TO_IN * ((crush[0] + crush[5]) * 0.5 + sum(crush[1:5])) / 5

            # NASS DV
            NASS_dv = float(total_dv) * KMPH_TO_MPH  # Convert to mph

            voi_curb_wgt *= KG_TO_LBS  # Convert to lbs
            a_curb_wgt = alt_data["a_curb_wgt"]
            NASS_vc = NASS_dv / (a_curb_wgt / (voi_curb_wgt + a_curb_wgt))

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
                    vehicle_num=event["voi"],
                    event_num=event["event_num"],
                    make=veh_ext_form.find("Make").text,
                    model=veh_ext_form.find("Model").text,
                    model_year=veh_ext_form.find("ModelYear").text,
                    curb_wgt=round(voi_curb_wgt, 2),
                    dmg_loc=cdc_event.find("DeformationLocation").text,
                    underride=cdc_event.find("OverUnderride").text,
                    edr=veh_ext_form.find("EDR").find("Obtained").text,
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
                    a_veh_num=event["alt_veh_num"],
                    a_veh_desc=event["alt_veh_desc"],
                    a_make=alt_data["a_make"],
                    a_model=alt_data["a_model"],
                    a_year=alt_data["a_year"],
                    a_curb_wgt=round(a_curb_wgt, 2),
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
