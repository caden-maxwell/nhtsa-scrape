import enum
from io import BytesIO
import json
import logging
import os
from pathlib import Path
import threading
import time
import requests

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, Qt

from bs4 import BeautifulSoup

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from .request_handler import RequestHandler, Request


class Priority(enum.Enum):
    '''Enum for request priorities. Lower integer is higher priority.'''
    ALL_COMBOS = 0
    MODEL_COMBO = 1
    IMAGE = 1
    CASE = 2
    CASE_LIST = 3


class ScrapeEngine(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    
    def __init__(self, search_params, image_set, case_limit):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.req_handler = RequestHandler()
        self.req_handler.response_received.connect(self.handle_response)
        self.CASE_URL = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
        self.CASE_LIST_URL = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"

        self.case_limit = case_limit
        self.image_set = image_set

        # Get default search payload and update with user input
        payload_path = Path(__file__).parent / "payload.json"
        with open(payload_path, "r") as f:
            self.search_payload = dict(json.load(f))
        self.search_payload.update(search_params)

        self.running = False
        self.current_page = 1
        self.cases_parsed = 0
        self.extra_cases = []
        self.final_page = False
        self.start_time = 0
        self.scrape_data = []
        self.timer = None

    def start(self):
        self.running = True
        self.started.emit()
        self.scrape()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_complete, Qt.ConnectionType.QueuedConnection)
        self.timer.start(1000) # Check every 1s if scrape is complete

    def stop(self):
        # Order matters here, otherwise the request handler will start making unnecessary case list requests once the individual cases are cleared
        self.req_handler.clear_queue(Priority.CASE_LIST.value)
        self.req_handler.clear_queue(Priority.CASE.value)

        self.running = False
        self.finished.emit()
        self.logger.debug(f"Scrape Data:\n{self.scrape_data}")
        self.logger.info(f"Scrape engine finished. {self.cases_parsed} cases parsed in {time.time() - self.start_time}s.")

    def limit_reached(self):
        return self.cases_parsed >= self.case_limit

    def check_complete(self):
        if not self.req_handler.contains(Priority.CASE.value) and not self.req_handler.get_ongoing_requests(Priority.CASE.value) and self.final_page:
            self.stop()
    
    def enqueue_extra_case(self):
        if self.extra_cases:
            caseid = self.extra_cases.pop()
            self.logger.debug(f"Enqueuing extra case: {caseid}")
            self.req_handler.enqueue_request(Request(f"{self.CASE_URL}{caseid}", priority=Priority.CASE.value))

    def scrape(self):
        self.start_time = time.time()
        self.logger.debug( f"""Scrape engine started with these params:
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

        request = Request(self.CASE_LIST_URL, method="POST", params=self.search_payload, priority=Priority.CASE_LIST.value)
        self.req_handler.enqueue_request(request)
    
    @pyqtSlot(int, str, int, str, str)
    def handle_response(self, priority, url, status_code, response_text, cookie):
        if priority == Priority.CASE_LIST.value:
            self.parse_case_list(url, response_text)
        elif priority == Priority.CASE.value:
            self.parse_case(url, response_text, cookie)
        elif priority == Priority.IMAGE.value:
            self.parse_image(url, status_code, response_text, cookie)
        else:
            self.logger.error(f"Scrape engine received response with invalid priority: {priority}.")
    
    def parse_case_list(self, url, response_text):
        if not response_text:
            self.logger.error(f"Received empty response from {url}.")
            self.final_page = True
            return

        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.stop()
            return

        soup = BeautifulSoup(response_text, "html.parser")
        page_dropdown = soup.find("select", id="ddlPage")
        if not page_dropdown:
            self.logger.warning(f"No cases found on page {self.search_payload['currentPage']}.")
            self.final_page = True
            return

        # Get all caseIDs on the current page
        case_ids = []
        tables = soup.find_all("table")
        if len(tables) > 1:
            table = tables[1] # The second table should have all the case links
            case_urls = [a["href"] for a in table.find_all("a")]
            case_ids = [url.split('=')[2] for url in case_urls]
        else:
            self.logger.warning(f"No cases found on page {self.search_payload['currentPage']}.")
            self.final_page = True
            return

        # Request each caseID on the current page
        self.extra_cases = case_ids[self.case_limit:]
        case_ids = case_ids[:self.case_limit]
        self.logger.info(f"Requesting {len(case_ids)} cases from page {self.current_page}...")
        for case_id in case_ids:
            self.req_handler.enqueue_request(Request(f"{self.CASE_URL}{case_id}", priority=Priority.CASE.value))

        total_pages = int(page_dropdown.find_all("option")[-1].text)
        if self.current_page == total_pages:
            self.logger.debug("Last page reached.")
            self.final_page = True
            return
        
        self.current_page += 1
        self.search_payload["currentPage"] = self.current_page
        self.logger.debug(f"Queueing page {self.current_page}...")


        self.req_handler.enqueue_request(Request(self.CASE_LIST_URL, method="POST", params=self.search_payload, priority=Priority.CASE_LIST.value))

    def parse_case(self, url, response_text, cookie):
        if not response_text:
            self.logger.error(f"Received empty response from {url}.")
            self.enqueue_extra_case()
            return
        
        if self.limit_reached():
            self.logger.debug("Case limit reached.")
            self.stop()
            return

        case_xml = BeautifulSoup(response_text, "xml")

        caseid = case_xml.find('CaseForm').get('caseID')
        summary = case_xml.find("Summary").text
        print("\n=========================================")
        print(f"Case ID: {caseid}")
        print(f"Summary: {summary}")

        make = int(self.search_payload["ddlMake"])
        model = int(self.search_payload["ddlModel"])
        start_year = int(self.search_payload["ddlStartModelYear"])
        end_year = 9999 if (year := int(self.search_payload["ddlEndModelYear"])) == -1 else year

        make_match = lambda veh_sum: make == int(veh_sum.find("Make").get("value")) or make == -1
        model_match = lambda veh_sum: model == int(veh_sum.find("Model").get("value")) or model == -1
        year_match = lambda veh_sum: start_year <= int(veh_sum.find("Year").text) <= end_year

        vehicle_nums = [
            int(veh_summary.get("VehicleNumber"))
            for veh_summary in case_xml.find_all("VehicleSum")
            if make_match(veh_summary) and model_match(veh_summary) and year_match(veh_summary)
        ]

        if not vehicle_nums: 
            print('No matching vehicles found.')
            self.enqueue_extra_case()
            return
        print(f"Vehicle numbers: {vehicle_nums}")

        veh_amount = int(case_xml.find("NumberVehicles").text)
        key_events = [
            {
                'en': int(event['EventNumber']),
                'voi': voi,
                'an': an,
            }
            for voi in vehicle_nums
            for event in case_xml.find_all("EventSum")
            if (an := self.get_an(voi, event, veh_amount)) # Add event to key_events only if 'an' is truthy.
        ]
        print(f"Key events: {key_events}")

        img_num = ''

        veh_ext_forms = case_xml.find("VehicleExteriorForms")
        gen_veh_forms = case_xml.find("GeneralVehicleForms")

        failed_events = 0
        for event in key_events:
            print(f"Event: {event}")

            veh_ext_form = veh_ext_forms.find("VehicleExteriorForm", {"VehicleNumber": event['voi']})
            if not veh_ext_form:
                print(f"No VehicleExteriorForm found for vehicle {event['voi']}.")
                failed_events += 1
                continue

            cdc_event = veh_ext_form.find("CDCevent", {"eventNumber": event['en']})
            tot = None
            lat = None
            lon = None
            if cdc_event:
                tot = int(cdc_event.find("Total")['value'])
                lat = int(cdc_event.find("Lateral")['value'])
                lon = int(cdc_event.find("Longitudinal")['value'])
                print(f"Total: {tot}, Longitudinal: {lon}, Lateral: {lat}")
            else:
                print(f"No CDCevent found for event {event['en']}.")

            crush_object = None
            for obj in veh_ext_form.find_all("CrushObject"):
                if event['en'] == int(obj.find("EventNumber").text):
                    crush_object = obj
                    break

            if not crush_object:
                print(f"No CrushObject found for event {event['en']}.")
                failed_events += 1
                continue

            avg_c1 = float(crush_object.find("AVG_C1")['value'])
            smash_l = None
            final_crush = None
            if avg_c1 >= 0:
                final_crush = [
                    avg_c1,
                    float(crush_object.find("AVG_C2")['value']),
                    float(crush_object.find("AVG_C3")['value']),
                    float(crush_object.find("AVG_C4")['value']),
                    float(crush_object.find("AVG_C5")['value']),
                    float(crush_object.find("AVG_C6")['value'])
                ]
                smash_l = crush_object.find("SMASHL")['value']
            else:
                print('No crush in file')
                failed_events += 1
                continue
            print(f"Crush: {final_crush}, Smash: {smash_l}")

            # VOI Info
            temp = {
                'summary': summary,
                'caseid': caseid,
                'casenum': case_xml.find("Case")['CaseStr'],
                'vehnum': veh_ext_form['VehicleNumber'],
                'year': veh_ext_form.find("ModelYear").text,
                'make': veh_ext_form.find("Make").text,
                'model': veh_ext_form.find("Model").text,
                'curbweight': float(veh_ext_form.find("CurbWeight").text),
                'damloc': veh_ext_form.find("DeformationLocation").text,
                'underride': veh_ext_form.find("OverUnderride").text,
                'edr': veh_ext_form.find("EDR").text,
                'total_dv': float(tot),
                'long_dv': float(lon),
                'lateral_dv': float(lat),
                'smashl': float(smash_l),
                'crush': final_crush,
            }

            # Alternate Vehicle Info
            temp['a_vehnum'] = event['an']
            alt_ext_form = veh_ext_forms.find('VehicleExteriorForm', {'VehicleNumber': event['an']})
            alt_ext_form = alt_ext_form if alt_ext_form else gen_veh_forms.find('GeneralVehicleForm', {'VehicleNumber': event['an']})

            if alt_ext_form:
                alt_temp = {
                    'a_year': alt_ext_form.find("ModelYear").text,
                    'a_make': alt_ext_form.find("Make").text,
                    'a_model': alt_ext_form.find("Model").text,
                    'a_curbweight': float(curbweight) if (curbweight := alt_ext_form.find("CurbWeight").text).isnumeric() else temp['curbweight'],
                }
                damloc = alt_ext_form.find("DeformationLocation") 
                alt_temp['a_damloc'] = damloc.text if damloc else '--'
            else:
                alt_temp = {
                    'a_year': '--',
                    'a_make': '--',
                    'a_model': '--',
                    'a_curbweight': 99999.0,
                    'a_damloc': '--'
                }
            temp.update(alt_temp)
            temp['image'] = img_num
            self.scrape_data.append(temp)

        if failed_events >= len(key_events):
            print(f"Insufficient data for caseID {caseid}.")
            self.enqueue_extra_case()
            return

        self.cases_parsed += 1
        self.check_complete()

    def parse_image(self, url, status_code, response_text, cookie):
        return
        img_form = case_xml.find('IMGForm')
        if not img_form:
            print('No ImgForm found.')
            return

        veh_img_areas = {
            'F': 'Front', 
            'B': 'Back', 
            'L': 'Left', 
            'R': 'Right', 
            'FL': 'Frontleftoblique', 
            'FR': 'Backleftoblique', 
            'BL': 'Frontrightoblique', 
            'BR': 'Backrightoblique'
        }

        img_set_lookup = {}
        for k,v in veh_img_areas.items():
            img_set_lookup[k] = [(img.text, img['version']) for img in img_form.find('Vehicle', {"VehicleNumber": event['voi']}).find(v).find_all('image')]

        image_set = image_set.split(' ')[0]
        img_elements = img_set_lookup.get(image_set, [])
        
        if not img_elements:
            print(f"No images found for image set {image_set}. Attempting to set to defaults...")
            veh_dmg_areas = {
                2: img_set_lookup['F'],
                5: img_set_lookup['B'],
                4: img_set_lookup['L'],
                3: img_set_lookup['R'],
            }
            img_elements = veh_dmg_areas.get(int(payload["ddlPrimaryDamage"]), [])

        fileName = 'i'
        while True:
            for img_element in img_elements:
                img_url = 'https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID=' + str(img_element[0]) + '&CaseID='+ caseid + '&Version=' + str(img_element[1])
                print(f"Image URL: {img_url}")

                cookie = {"Cookie": response.headers['Set-Cookie']}
                response = requests.get(img_url, headers=cookie)
                img = Image.open(BytesIO(response.content))
                draw = ImageDraw.Draw(img)
                draw.rectangle(((0, 0), (300, 30)), fill="white")
                tot_mph = str(float(tot)*0.6214)
                img_text = 'Case No: ' + caseid + ' - NASS DV: ' + tot_mph
                draw.text((0, 0),img_text,(220,20,60),font=ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 24))
                img.show()
                g = input("Select: [NE]xt Image, [SA]ve Image, [DE]lete Case, [FT]ront, [FL]ront Left, [LE]ft,"
                        "[BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right: ")
                
                def check_image_set(image_set):
                    if not self.image_set:
                        self.image_set = img_set_lookup['F']
                        if 'F' in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup['F']
                        elif 'R' in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup['R']
                        elif 'B' in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup['B']
                        elif 'L' in self.search_payload["ddlPrimaryDamage"]:
                            self.image_set = img_set_lookup['L']
                        print('Empty Image Set')
                        return self.image_set
                    else: return self.image_set

                if 'sa' in g.lower():
                    caseid_path = os.getcwd() + '/' +  self.search_payload["ddlStartModelYear"] + '_' + self.search_payload["ddlEndModelYear"] + '_' + self.search_payload["ddlMake"] + "_" + self.search_payload["ddlModel"] + '_' + self.search_payload["ddlPrimaryDamage"]
                    if not os.path.exists(caseid_path):
                        os.makedirs(caseid_path)
                    os.chdir(caseid_path)

                    img_num = str(img_element[0])
                    fileName = caseid_path + '//' + img_num + '.jpg'
                    img.save(fileName)
                    g = 'de'
                    break
                elif 'ne' in g.lower():
                    continue
                elif 'de' in g.lower():
                    break
                elif 'ft' in g.lower():
                    img_elements = check_image_set(front_images)
                    break
                elif 'fr' in g.lower():
                    img_elements = check_image_set(frontright_images)
                    break
                elif 'ri' in g.lower():
                    img_elements = check_image_set(right_images)
                    break
                elif 'br' in g.lower():
                    img_elements = check_image_set(backright_images) 
                    break
                elif 'ba' in g.lower():
                    img_elements = check_image_set(back_images)
                    break
                elif 'bl' in g.lower():
                    img_elements = check_image_set(backleft_images)
                    break
                elif 'le' in g.lower():
                    img_elements = check_image_set(left_images)
                    break
                elif 'fl' in g.lower():
                    img_elements = check_image_set(frontleft_images)
                    break
                img.close()
            if 'de' in g.lower():
                break

    def calculations(self):
        return
        file = f"{self.search_payload['ddlStartModelYear']}_{self.search_payload['ddlEndModelYear']}_{self.search_payload['ddlMake']}_{self.search_payload['ddlModel']}_{self.search_payload['ddlPrimaryDamage']}.csv"

        self.logger.info("\n" + json.dumps(contents, indent=4))
        x = []
        y_nass = []
        y_total = []

        return
        for cse in contents:
            #average crush in inches
            c_bar = 0.393701*((cse['crush'][0]+cse['crush'][5])*0.5+sum(cse['crush'][1:4]))/5.0
            cse['c_bar'] = c_bar
            #NASS DV in MPH
            NASS_dv = cse['total_dv']*0.621371
            cse['NASS_dv'] = NASS_dv
            #Vehicle Weights in LBS
            voi_wt = cse['curbweight']*2.20462
            a_wt = cse['a_curbweight']*2.20462
            NASS_vc = NASS_dv/(a_wt/(voi_wt+a_wt))
            cse['NASS_vc'] = NASS_vc
            e = 0.5992*np.exp(-0.1125*NASS_vc+0.003889*NASS_vc**2-0.0001153*NASS_vc**3)
            cse['e'] = e
            TOT_dv = NASS_dv*(1.0+e)
            cse['TOT_dv'] = TOT_dv
            x.append(c_bar)
            y_nass.append(NASS_dv)
            y_total.append(TOT_dv)
            #pdb.set_trace()
        slope, intercept = np.polyfit(x, y_nass, 1)

        i = []
        [i.append(cse['image']) for cse in contents]
        df_original = pd.DataFrame(contents,index = i)

        #field_names = ["summary","caseid","vehnum","year","make","model","curbweight","damloc","underride","total_dv","long_dv",
        #               "lateral_dv","smashl","crush","a_vehnum","a_year","a_make","a_model","a_curbweight", "image","c_bar","NASS_dv",
        #               "NASS_vc","e","TOT_dv"]
        #with open(file, 'w') as f:
        #    w = csv.DictWriter(f, fieldnames=field_names)
        #    w.writeheader()
        #    w.writerows(contents)

        df = df_original[['caseid','c_bar','NASS_dv','NASS_vc','TOT_dv']]
        df_original = df_original[['caseid', 'casenum', 'vehnum', 'year', 'make', 'model', 'curbweight',
            'damloc', 'underride','edr', 'total_dv', 'long_dv', 'lateral_dv', 'smashl',
            'crush', 'a_vehnum', 'a_year', 'a_make', 'a_model', 'a_curbweight',
            'image', 'c_bar', 'NASS_dv', 'NASS_vc', 'e', 'TOT_dv','summary', ]]
                
        # Scatter plots.
        dfn = df.apply(pd.to_numeric, errors='coerce')

        # dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
        dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c='r',figsize=(16,12))

        fit=np.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
        fit_e=np.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

        slope = fit[0]
        slope_e = fit_e[0]

        intercept = fit[1]
        intercept_e = fit_e[1]

        s_eq = 'Y = ' + str(round(slope,1)) + 'X + ' + str(round(intercept,1))
        s_eq_e = 'Y = ' + str(round(slope_e,1)) + 'X + ' + str(round(intercept_e,1))

        # regression lines
        plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color='darkblue', linewidth=2)
        #plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

        predict = np.poly1d(fit)
        predict_e = np.poly1d(fit_e)
        r2 = str(round((r2_score(dfn.NASS_dv, predict(dfn.c_bar))),2))
        r2_e = str(round((r2_score(dfn.TOT_dv, predict_e(dfn.c_bar))),2))

        # legend, title and labels.
        #plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq, 'Total, ' + 'r$\mathregular{^2}$ value = ' + r2_e + ' - ' + s_eq_e], fontsize=14)
        plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq], fontsize=14)
        plt.xlabel('Crush (inches)', size=24)
        plt.ylabel('Change in Velocity (mph)', size=24);
        for i, label in enumerate(df['caseid']):
            plt.text(dfn.c_bar[i], dfn.NASS_dv[i],label)  
        #for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        plt.savefig(caseid_path + '//' + 'NASS_Analysis.png', dpi=150)

        crush_est = np.array([0, 1.0])
        print(predict(crush_est))
        print(predict_e(crush_est))
        print(df)

        # Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in df.index:
            s = 'Caseid: ' + str(df.loc[i].caseid) + '. NASSDV = ' + str(df.loc[i].NASS_dv)
            img = Image.open(caseid_path + '//' + i + '.jpg')
            draw = ImageDraw.Draw(img)
            #draw.text((0, 0),s,(220,20,60),font=font)
            img.show()
            #plt.text(25, 25, s, fontsize=18, bbox=dict(facecolor='white', edgecolor='red', linewidth=2))
            g = input(s + ' ' "Select: [SA]ve case, [DE]lete Case, [ST]op: ")
            img.close()
            if 'de' in g.lower():
                df = df.drop(index = i)
                df_original = df_original.drop(index = i)
                continue
            elif 'st' in g.lower():
                break
            else:
                continue
        # Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            
        dfn = df.apply(pd.to_numeric, errors='coerce')

        #dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
        dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c='r',figsize=(16,12))

        fit=np.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
        fit_e=np.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

        slope = fit[0]
        slope_e = fit_e[0]

        intercept = fit[1]
        intercept_e = fit_e[1]

        s_eq = 'Y = ' + str(round(slope,1)) + 'X + ' + str(round(intercept,1))
        s_eq_e = 'Y = ' + str(round(slope_e,1)) + 'X + ' + str(round(intercept_e,1))

        # regression lines
        plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color='darkblue', linewidth=2)
        #plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

        predict = np.poly1d(fit)
        predict_e = np.poly1d(fit_e)
        r2 = str(round((r2_score(dfn.NASS_dv, predict(dfn.c_bar))),2))
        r2_e = str(round((r2_score(dfn.TOT_dv, predict_e(dfn.c_bar))),2))

        # legend, title and labels.
        #plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq, 'Total, ' + 'r$\mathregular{^2}$ value = ' + r2_e + ' - ' + s_eq_e], fontsize=14)
        plt.legend(labels=['NASS, ' + 'r$\mathregular{^2}$ value = ' + r2 + ' - ' + s_eq], fontsize=14)
        plt.xlabel('Crush (inches)', size=24)
        plt.ylabel('Change in Velocity (mph)', size=24);
        for i, label in enumerate(df['caseid']):
            plt.text(dfn.c_bar[i], dfn.NASS_dv[i],label)  
        #for i, label in enumerate(df.index):
        #    plt.text(dfn.c_bar[i], dfn.TOT_dv[i],label)

        plt.savefig(caseid_path + '//' + 'NASS_Analysis.png', dpi=150)

        crush_est = np.array([0, 1.0])
        print(predict(crush_est))
        print(predict_e(crush_est))
        print(df)

        df_original.to_csv(caseid_path + '//' + file)
        f = open(caseid_path + '//' + file,'a')
        writer = csv.writer(f)

        csestr = ''
        end = len(df['caseid'])-1
        for i in range(len(df['caseid'])):
            cnum = df['caseid'].iloc[i]
            if i == end:
                csestr = csestr + 'and ' + cnum + '.'
            else:
                csestr = csestr + cnum + ', '

        temp1 = df.sort_values(by=['NASS_dv'])
        minval = str(round(temp1.iloc[0]['NASS_dv'],1))
        mincase = temp1.iloc[0]['caseid']
        maxval = str(round(temp1.iloc[end]['NASS_dv'],1))
        maxcase = temp1.iloc[end]['caseid']

        dvstr = ' Among these cases, the changes in velocity ranged from as low as ' + minval + ' mph (' + mincase + ') to as high as ' + maxval + ' mph (' + maxcase + ').'

        par = csestr + dvstr
        writer.writerows([[],[par]])
        f.close()

    def get_an(self, voi: int, event: BeautifulSoup, num_vehicles: int):

        # For whatever reason, the area of damage and contacted area of damage values are off by 1 in the XML viewer
        area_of_dmg = int(event.find('AreaOfDamage')['value']) - 1
        contacted_aod = int(event.find('ContactedAreaOfDamage')['value']) - 1

        contacted = event.find("Contacted")
        vehicle_number = int(event['VehicleNumber'])

        primary_damage = int(self.search_payload["ddlPrimaryDamage"])
        primary_dmg_match = primary_damage == area_of_dmg if primary_damage != -1 else True
        contacted_dmg_match = primary_damage == contacted_aod if primary_damage != -1 else True

        if voi == vehicle_number and primary_dmg_match: # If the voi is the primary vehicle, return the contacted vehicle/object as the an
            if int(contacted['value']) > num_vehicles:
                return contacted.text
            else:
                return int(contacted['value'])
        elif str(voi) in contacted.text and contacted_dmg_match: # If the voi is the contacted vehicle, return the primary vehicle as the an
            return vehicle_number 
        
        return 0 # voi not involved in this event

# def get_r2(self, x, y):
#     slope, intercept = np.polyfit(x, y, 1)
#     r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
#     return r_squared
