# from io import BytesIO
import json
import logging
# import os
from pathlib import Path
import traceback
# import requests

from PyQt6.QtCore import QThread

from bs4 import BeautifulSoup
# from PIL import Image
# from PIL import ImageFont
# from PIL import ImageDraw 

from .request_handler import WebRequestHandler, Request

class ScrapeEngine(QThread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.CASES_PER_PAGE = 40
        self.case_limit = self.CASES_PER_PAGE
        self.image_set = "All"
        self.request_handler = WebRequestHandler()

        # Get default search payload
        payload_path = Path(__file__).parent / "payload.json"
        with open(payload_path, "r") as f:
            self.search_payload = json.load(f)

    def update_payload(self, key, val):
        self.search_payload[key] = val
        self.logger.info(f"{key} updated to '{val}'.")

    def set_case_limit(self, limit):
        self.case_limit = limit
        self.logger.info(f"Case limit updated to '{limit}'.")
        
    def change_image_set(self, image_set):
        self.image_set = image_set
        self.logger.info(f"Image set updated to '{image_set}'.")

    def run(self):
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

        self.request_handler.clear()
        payload = self.search_payload.copy() # Copy payload to avoid modifying while scraping
        case_limit = self.case_limit
        image_set = self.image_set

        request = Request("https://crashviewer.nhtsa.dot.gov/LegacyCDS", method="POST", params=payload)
        response = self.request_handler.send_request(request)

        if not response:
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        page_dropdown = soup.find("select", id="ddlPage")
        if not page_dropdown:
            self.logger.error("No cases found.")
            return
        total_pages = int(page_dropdown.find_all("option")[-1].text)
        remaining = case_limit
        page_num = 1
        responses = []
        while len(responses) < case_limit:
            remaining = case_limit - len(responses)
            case_ids = self.get_case_ids(soup)[:remaining]

            url = "https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid="
            self.request_handler.clear()
            self.request_handler.queue_requests([Request(url + case_id) for case_id in case_ids])
            self.logger.debug(f"Requesting cases from page {page_num}...")
            self.request_handler.send_requests()
            responses.extend(self.request_handler.get_responses())

            if self.isInterruptionRequested():
                break

            page_num += 1
            if page_num > total_pages:
                break

            payload["currentPage"] = page_num
            self.logger.debug(f"Requesting page {page_num}...")
            url = "https://crashviewer.nhtsa.dot.gov/LegacyCDS"
            response = self.request_handler.send_request(Request(url, method="POST", params=payload))
            if not response:
                break
            soup = BeautifulSoup(response.text, "html.parser")
        
        self.logger.info(f"Received {len(responses)} cases.")

        temp = {}
        contents = []
        file = f"{payload['ddlStartModelYear']}_{payload['ddlEndModelYear']}_{payload['ddlMake']}_{payload['ddlModel']}_{payload['ddlPrimaryDamage']}.csv"
        
        for response in responses:
            caseid = response
            cdc = []
            cdcevents = []
            tot = []
            lat = []
            lon = []
            final_crush = []
            crush_test = 1
            smash_l = []
            img_num = ''
            
            page = BeautifulSoup(response.text, "xml")
            print(f"Case ID: {page.find('CaseForm').get('caseID')}")
            summary = page.find("Summary").text
            print(f"Summary: {summary}")
            num_vehicles = int(page.find("NumberVehicles").text)
            print(f"Number of vehicles: {num_vehicles}")
            veh_ext_forms = page.findAll("VehicleExteriorForm")
            print(f"Number of vehicle exterior forms: {len(veh_ext_forms)}")
            gen_veh_forms = page.findAll("GeneralVehicleForm")
            print(f"Number of general vehicle forms: {len(gen_veh_forms)}")
            event_forms = page.findAll("EventSum")
            print(f"Number of event forms: {len(event_forms)}")

            ### Code works up to here ###

            veh_nums = []
            for gen_veh_form in gen_veh_forms:
                print("=========================================")
                print(f"General vehicle form: {gen_veh_form.get('VehicleNumber')}")

                make = int(gen_veh_form.find("Make").get("value"))
                model = int(gen_veh_form.find("Model").get("value"))
                model_year = int(gen_veh_form.find("ModelYear").text)
                print(f"Make: {make}, Model: {model}, Model Year: {model_year}")
                print(f"Payload make: {payload['ddlMake']}, Payload model: {payload['ddlModel']}, Payload model year: {payload['ddlStartModelYear']} - {payload['ddlEndModelYear']}")

                is_make = int(payload["ddlMake"]) == make
                is_model = int(payload["ddlModel"]) == model
                is_model_year = int(payload["ddlStartModelYear"]) <= model_year <= int(payload["ddlEndModelYear"])
                print(f"Is make: {is_make}, Is model: {is_model}, Is model year: {is_model_year}")

                if is_make and is_model and is_model_year:
                    print(f"Adding vehicle number {gen_veh_form.get('VehicleNumber')} to veh_nums")
                    veh_nums.append(gen_veh_form.get("VehicleNumber"))
            print("=========================================")
                    
            if not veh_nums: 
                print('No vehicle numbers found')
                continue

            tempevent = {}
            keyevents = []
            for voi in veh_nums:
                print(f"Vehicle of interest: {voi}")

                for event in event_forms:
                    print(f"Event number: {event['EventNumber']}")

                    area_of_dmg = int(event.find('AreaOfDamage')['value'])
                    contacted_aod = int(event.find('ContactedAreaOfDamage')['value'])
                    contacted = event.find("Contacted")

                    if voi in event['VehicleNumber'] and int(payload["ddlPrimaryDamage"]) == area_of_dmg:
                        if 'en' in tempevent:
                            if tempevent.get('en') == int(event['EventNumber']):

                                tempevent['en'] = int(event['EventNumber'])
                                tempevent['voi'] = voi
                                if int(contacted['value']) > num_vehicles:
                                    tempevent['an'] = contacted.text
                                else:
                                    tempevent['an'] = contacted['value']

                            else:
                                keyevents.append(tempevent)

                                tempevent['en'] = event['EventNumber']
                                tempevent['voi'] = voi
                                if int(contacted['value']) > num_vehicles:
                                    tempevent['an'] = contacted.text
                                else:
                                    tempevent['an'] = contacted['value']
                        else:
                            tempevent['en'] = event['EventNumber']
                            tempevent['voi'] = voi
                            if int(contacted['value']) > num_vehicles:
                                tempevent['an'] = contacted.text
                            else:
                                tempevent['an'] = contacted['value']

                    elif voi in contacted.text and int(payload["ddlPrimaryDamage"]) == contacted_aod:
                        if 'en' in tempevent:
                            if str(tempevent.get('en')) in event['EventNumber']:
                                tempevent['en'] = event['EventNumber']
                                tempevent['voi'] = voi
                                tempevent['an'] = event['VehicleNumber']
                            else:
                                keyevents.append(tempevent)
                                tempevent['en'] = event['EventNumber']
                                tempevent['voi'] = voi
                                tempevent['an'] = event['VehicleNumber']
                        else:
                            tempevent['en'] = event['EventNumber']
                            tempevent['voi'] = voi
                            tempevent['an'] = event['VehicleNumber']
            keyevents.append(tempevent)
            print(keyevents)

            for event in keyevents:
                image_set = []
                fileName = ''
                for x in range(len(veh_ext_forms)):
                    if event['voi'] in veh_ext_forms[x]['vehiclenumber']:
                        n_voi = x
                        cdcevents = veh_ext_forms[x].findAll("cdcevent")
                        crushobjects = veh_ext_forms[x].findAll("crushobject")
                        for cdc in cdcevents:
                            if event['en'] in cdc['eventnumber']:
                                tot = cdc.total['value']
                                lon = cdc.longitudinal['value']
                                lat = cdc.lateral['value']
                        for crush in crushobjects:
                            if event['en'] in crush.eventnumber.text:
                                #pdb.set_trace()
                                if float(crush.avg_c1['value'])>=0:
                                    final_crush = [float(crush.avg_c1['value']),float(crush.avg_c2['value']),float(crush.avg_c3['value']),
                                                float(crush.avg_c4['value']),float(crush.avg_c5['value']),float(crush.avg_c6['value'])]
                                    smash_l = crush.smashl['value']
                                else:
                                    crush_test = float(crush.avg_c1['value'])
                for x in range(len(gen_veh_forms)):
                    if event['an'] in gen_veh_forms[x]['vehiclenumber']:
                        n_an = x
                if crush_test<0: print('No crush in file')
                if crush_test>=0:
                    front_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).front.findAll('image')]
                    frontleft_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).frontleftoblique.findAll('image')]
                    left_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).left.findAll('image')]
                    backleft_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).backleftoblique.findAll('image')]
                    back_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).back.findAll('image')]
                    backright_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).backrightoblique.findAll('image')]
                    right_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).right.findAll('image')]
                    frontright_images = [(row.text,row['version']) for row in page.imgform.find('vehicle',{'vehiclenumber':event['voi']}).frontrightoblique.findAll('image')]       
                    # Need to make sure the right event/CDC is placed in the following variables. 
                    #print(extform[n_voi]['caseid'])
                    def check_image_set(image_set):
                        if not image_set:
                            if 'F' in payload["ddlPrimaryDamage"]:
                                image_set = front_images
                            elif 'R' in payload["ddlPrimaryDamage"]:
                                image_set = right_images
                            elif 'B' in payload["ddlPrimaryDamage"]:
                                image_set = back_images
                            elif 'L' in payload["ddlPrimaryDamage"]:
                                image_set = left_images
                            print('Empty Image Set')
                            return image_set
                        else: return image_set
                    with requests.session() as s:
                        if 'ft' in self.image_set.lower():
                            image_set = front_images
                        elif 'fr' in self.image_set.lower():
                            image_set = frontright_images
                        elif 'ri' in self.image_set.lower():
                            image_set = right_images
                        elif 'br' in self.image_set.lower():
                            image_set = backright_images
                        elif 'ba' in self.image_set.lower():
                            image_set = back_images
                        elif 'bl' in self.image_set.lower():
                            image_set = backleft_images
                        elif 'le' in self.image_set.lower():
                            image_set = left_images
                        elif 'fl' in self.image_set.lower():
                            image_set = frontleft_images
                        if not image_set:
                            if 'F' in payload["ddlPrimaryDamage"]:
                                image_set = front_images
                            elif 'R' in payload["ddlPrimaryDamage"]:
                                image_set = right_images
                            elif 'B' in payload["ddlPrimaryDamage"]:
                                image_set = back_images
                            elif 'L' in payload["ddlPrimaryDamage"]:
                                image_set = left_images  
                        while True:
                            for row in image_set:
                                img_url = 'https://crashviewer.nhtsa.dot.gov/nass-cds/GetBinary.aspx?Image&ImageID=' + str(row[0]) + '&CaseID='+ caseid + '&Version=' + str(row[1])
                                response = s.get(img_url)
                                img = Image.open(BytesIO(response.content))
                                draw = ImageDraw.Draw(img)
                                draw.rectangle(((0, 0), (300, 30)), fill="white")
                                tot_mph = str(float(tot)*0.6214)
                                img_text = 'Case No: ' + caseid + ' - NASS DV: ' + tot_mph
                                draw.text((0, 0),img_text,(220,20,60),font=ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 24))
                                img.show()
                                g = input("Select: [NE]xt Image, [SA]ve Image, [DE]lete Case, [FT]ront, [FL]ront Left, [LE]ft,"
                                        "[BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right: ")
                                if 'sa' in g.lower():
                                    caseid_path = os.getcwd() + '/' +  payload["ddlStartModelYear"] + '_' + payload["ddlEndModelYear"] + '_' + payload["ddlMake"] + "_" + payload["ddlModel"] + '_' + payload["ddlPrimaryDamage"]
                                    if not os.path.exists(caseid_path):
                                        os.makedirs(caseid_path)
                                    os.chdir(caseid_path)
        
                                    img_num = str(row[0])
                                    fileName = caseid_path + '//' + img_num + '.jpg'
                                    img.save(fileName)
                                    g = 'de'
                                    break
                                elif 'ne' in g.lower():
                                    continue
                                elif 'de' in g.lower():
                                    break
                                elif 'ft' in g.lower():
                                    image_set = check_image_set(front_images)
                                    break
                                elif 'fr' in g.lower():
                                    image_set = check_image_set(frontright_images)
                                    break
                                elif 'ri' in g.lower():
                                    image_set = check_image_set(right_images)
                                    break
                                elif 'br' in g.lower():
                                    image_set = check_image_set(backright_images) 
                                    break
                                elif 'ba' in g.lower():
                                    image_set = check_image_set(back_images)
                                    break
                                elif 'bl' in g.lower():
                                    image_set = check_image_set(backleft_images)
                                    break
                                elif 'le' in g.lower():
                                    image_set = check_image_set(left_images)
                                    break
                                elif 'fl' in g.lower():
                                    image_set = check_image_set(frontleft_images)
                                    break
                                img.close()
                            if 'de' in g.lower():
                                break
                    if not len(fileName) == 0:
                        temp = {'summary':summary}
                        temp['caseid'] = veh_ext_forms[n_voi]['caseid']
                        temp['casenum'] = page.case['casestr']
                        temp['vehnum'] = veh_ext_forms[n_voi]['vehiclenumber']
                        temp['year'] = veh_ext_forms[n_voi].modelyear.text
                        temp['make'] = veh_ext_forms[n_voi].make.text
                        temp['model'] = veh_ext_forms[n_voi].model.text
                        temp['curbweight'] = float(veh_ext_forms[n_voi].curbweight.text)
                        temp['damloc'] = veh_ext_forms[n_voi].deformationlocation.text
                        temp['underride'] = veh_ext_forms[n_voi].overunderride.text
                        temp['edr'] = veh_ext_forms[n_voi].edr.text
                        #Check correct CDC
                        temp['total_dv'] = float(tot)
                        temp['long_dv'] = float(lon)
                        temp['lateral_dv'] = float(lat)
                        temp['smashl'] = float(smash_l)
                        temp['crush'] = final_crush
                        #Alternate Vehicle Info
                        if event['an'].isnumeric():
                            temp['a_vehnum'] = gen_veh_forms[n_an]['vehiclenumber']
                            temp['a_year'] = gen_veh_forms[n_an].modelyear.text
                            temp['a_make'] = gen_veh_forms[n_an].make.text
                            temp['a_model'] = gen_veh_forms[n_an].model.text
                            if 'Unk' in gen_veh_forms[n_an].curbweight.text:
                                temp['a_curbweight'] = temp['curbweight']
                            else:
                                temp['a_curbweight'] = float(gen_veh_forms[n_an].curbweight.text)
                        else:
                            temp['a_vehnum'] = event['an']
                            temp['a_year'] = '--'
                            temp['a_make'] = '--'
                            temp['a_model'] = '--'
                            temp['a_curbweight'] = 99999.0
                        temp['image'] = img_num
                        #temp['a_damloc'] = genvehform[n_an].deformationlocation.text
                        contents.append(temp)
                        print(temp)
                        temp = {}
                
    def get_case_ids(self, soup: BeautifulSoup):
        tables = soup.find_all("table")
        if len(tables) > 1:
            table = tables[1] # The second table should have all the case links
            case_urls = [a["href"] for a in table.find_all("a")]
            return [url.split('=')[2] for url in case_urls]
        return []

    def requestInterruption(self):
        self.request_handler.stop()
        return super().requestInterruption()
