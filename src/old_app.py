from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import matplotlib.pyplot as plt
import pandas
from sklearn.metrics import r2_score
import csv 
import os
import numpy
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO

#Primary Damage Options
#<="-1">All<>,
# <="2">F Front<>,
# <="5">B Back (Rear)<>,
# <="4">L Left Side<>,
# <="3">R Right Side<>,
# <="6">T Top<>,D
# <="7">U Undercarriage<>,
# <="8">9 Unknown<>

#Secondary Damage Options
#<="">All<>,
# <="9">D Distributed - side or end<>,
# <="10">L Left - front or rear<>,
# <="11">C Center - front or rear<>,
# <="12">R Right - front or rear<>,
# <="13">F Side Front - left or right<>,
# <="14">P Side center section L or R<>,
# <="15">B Side Rear - left or right<>,
# <="16">Y Side (F + P) OR End (L + C)<>,
# <="17">Z Side (P + B) OR End (C + R)<>,

# Default Image Set: [FT]ront, [FL]ront Left, [LE]ft, [BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right

istartyear = '2011'
iendyear = '2016'
imake = 'CHRYSLER'
imodel = '300'
idvfrom = "0"
idvto = "159"
ipdamage = 'L'
isdamage = 'ALL'
default_imageset = 'All'
multi_analysis = True

default_path = os.getcwd()

# Specify the URL
urlpage = 'https://crashviewer.nhtsa.dot.gov/LegacyCDS/Search' 

# run firefox webdriver from executable path of your choice
options = Options()
options.add_argument("-headless")
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()),options=options)
print("Firefox Headless Browser Invoked")

# get web page
driver.get(urlpage)

init = soup(driver.page_source,'html.parser')

make_menu =driver.find_element("xpath","//*[@id='ddlMake']")
model_menu = driver.find_element("xpath",'//*[@id="ddlModel"]')

select_make = Select(make_menu)
make_options = select_make.options
for row in make_options:
    if imake in row.text:
        make = row.text
        select_make.select_by_visible_text(make)

select_model = Select(model_menu)
model_options = select_model.options
for row in model_options:
    if imodel in row.text:
        print(row.text)
        model = row.text
        select_model.select_by_visible_text(model)

primary_menu = driver.find_element("xpath","//*[@id='ddlPrimaryDamage']")
subsection_menu = driver.find_element("xpath","//*[@id='lSecondaryDamage']")

select_primary = Select(primary_menu)
primary_options = select_primary.options
for row in primary_options:
    if ipdamage in row.text:
        select_primary.select_by_visible_text(row.text)
        
select_subsection = Select(subsection_menu)
subsection_options = select_subsection.options
for row in subsection_options:
    if isdamage in row.text:
        select_subsection.select_by_visible_text(row.text)
        
test_yr_min = int(istartyear)
test_yr_max = int(iendyear)
test_make = make
test_model = model
test_dl = ipdamage

# Get Search Results
select_start_year = Select(driver.find_element("name",'ddlStartModelYear'))
                    
select_start_year.select_by_visible_text(istartyear)

select_end_year = Select(driver.find_element("name",'ddlEndModelYear'))
select_end_year.select_by_visible_text(iendyear)

text_DVFrom = driver.find_element("name",'tDeltaVFrom')
text_DVFrom.send_keys(idvfrom)

text_DVTo = driver.find_element("name",'tDeltaVTo')
text_DVTo.send_keys(idvto)

# Click the Search Button box
driver.find_element("name",'btnSubmit').click()



links_page = soup(driver.page_source,features='xml')

all_caseid = []
page_menu = driver.find_element("xpath","//*[@id='ddlPage']")
select_page = Select(page_menu)
page_options = select_page.options

for i in range(len(page_options)):
    page_menu = driver.find_element("xpath","//*[@id='ddlPage']")
    select_page = Select(page_menu)
    page_options = select_page.options
    select_page.select_by_visible_text(str(i+1))
    links_page = soup(driver.page_source,'html.parser')
    all_links = [a['href'] for a in links_page.findAll('a',href=True)]
    links = [row for row in all_links if 'crashviewer' in row]
    case_id = [row.split('=')[2] for row in links]
    all_caseid = all_caseid + case_id

print('Number of cases:')
print(len(all_caseid))

driver.quit()

temp = {}

if multi_analysis:
    if 'contents' not in locals():
        contents = []
    if 'file' not in locals():
        file = istartyear + '_' + iendyear + '_' + imake + '_'  + imodel + '_' + test_dl + '.csv'
else:
    contents = []
    file = istartyear + '_' + iendyear + '_' + imake + '_'  + imodel + '_' + test_dl + '.csv'

font = ImageFont.truetype(r"C:\Windows\Fonts\Arial.ttf", 24)
def add_event(tempevent, event, voi, chk):
    """Chk variable checks to see if voi is in vehiclenumber (1) or contacted (0)"""
    tempevent['en'] = event['eventnumber']
    tempevent['voi'] = voi
    if chk:
        if int(event.contacted['value']) > int(numvehicles):
            tempevent['an'] = event.contacted.text
        else:
            tempevent['an'] = event.contacted['value']
    else:
        tempevent['an'] = event['vehiclenumber']
    return tempevent
for caseid2 in list(enumerate(all_caseid)):
    ind,caseid = caseid2
    vn = []
    en = []
    an = []
    cdc = []
    cdcevents = []
    crushevents = []
    tot = []
    lat = []
    lon = []
    final_crush = []
    crush_test = 1
    smash_l = []
    keyevents = []
    tempevent = {}
    img_num = ''
    print(f"{caseid}: {ind+1}/{len(all_caseid)}")

    begin1 = 'https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?GetXML&caseid='
    end1 = '&year=&transform=0&docInfo=0'
    case_url=begin1+caseid+end1
    page = soup(uReq(case_url).read(),features="lxml")
    summary = page.summary.text
    numevents = page.events.text
    numvehicles = page.vehicles.numbervehicles.text
    extform = page.vehicleexteriorforms.findAll("vehicleexteriorform")
    genvehform = page.findAll("generalvehicleform")
    eventforms = page.findAll("eventsum")
    imgforms = page.imgform.findAll('vehicle')
    vn = [genvehform[x]['vehiclenumber'] for x in range(len(genvehform)) if (test_make in genvehform[x].make.text 
          and imodel in genvehform[x].model.text and test_yr_min <= int(genvehform[x].modelyear.text) <= test_yr_max)]
    if not vn: 
        print('VN not found')
        continue
    print(vn)
    print(eventforms)
    for voi in vn:
        for event in eventforms:
            if (voi in event['vehiclenumber'] and test_dl in event.areaofdamage.text):
                if 'en' in tempevent:
                    if str(tempevent.get('en')) in event['eventnumber']:
                        tempevent = add_event(tempevent,event,voi,chk=1)
                    else:
                        keyevents.append(tempevent)
                        tempevent = add_event(tempevent,event,voi,chk=1)
                else:
                    tempevent = add_event(tempevent,event,voi,chk=1)
            elif voi in event.contacted.text and test_dl in event.contactedareaofdamage.text:
                if 'en' in tempevent:
                    if str(tempevent.get('en')) in event['eventnumber']:
                        tempevent = add_event(tempevent,event,voi,chk=0)
                    else:
                        keyevents.append(tempevent)
                        tempevent = add_event(tempevent,event,voi,chk=0)
                else:
                    tempevent = add_event(tempevent,event,voi,chk=0)
    keyevents.append(tempevent)
    for event in keyevents:
        image_set = []
        fileName = ''
        for x in range(len(extform)):
            print("event['voi']")
            if event['voi'] in extform[x]['vehiclenumber']:
                n_voi = x
                cdcevents = extform[x].findAll("cdcevent")
                crushobjects = extform[x].findAll("crushobject")
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
        for x in range(len(genvehform)):
            if event['an'] in genvehform[x]['vehiclenumber']:
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
                    if 'F' in ipdamage:
                        image_set = front_images
                    elif 'R' in ipdamage:
                        image_set = right_images
                    elif 'B' in ipdamage:
                        image_set = back_images
                    elif 'L' in ipdamage:
                        image_set = left_images
                    print('Empty Image Set')
                    return image_set
                else: return image_set
            with requests.session() as s:
                url = 'https://crashviewer.nhtsa.dot.gov/nass-cds/CaseForm.aspx?xsl=main.xsl&CaseID=' + str(extform[n_voi]['caseid'])
                r = s.get(url)
                #try: image_set
                #except NameError: image_set = None
                #if image_set is None:
                default_imageset
                if 'ft' in default_imageset.lower():
                    image_set = front_images
                elif 'fr' in default_imageset.lower():
                    image_set = frontright_images
                elif 'ri' in default_imageset.lower():
                    image_set = right_images
                elif 'br' in default_imageset.lower():
                    image_set = backright_images
                elif 'ba' in default_imageset.lower():
                    image_set = back_images
                elif 'bl' in default_imageset.lower():
                    image_set = backleft_images
                elif 'le' in default_imageset.lower():
                    image_set = left_images
                elif 'fl' in default_imageset.lower():
                    image_set = frontleft_images
                if not image_set:
                    if 'F' in ipdamage:
                        image_set = front_images
                    elif 'R' in ipdamage:
                        image_set = right_images
                    elif 'B' in ipdamage:
                        image_set = back_images
                    elif 'L' in ipdamage:
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
                        draw.text((0, 0),img_text,(220,20,60),font=font)
                        img.show()
                        user_in = input("Select: [NE]xt Image, [SA]ve Image, [DE]lete Case, [FT]ront, [FL]ront Left, [LE]ft,"
                                  "[BL]ack Left, [BA]ck, [BR]ack Right, [RI]ght, [FR]ront Right: ")
                        if 'sa' in user_in.lower():
                            # write `content` to file
                            if multi_analysis:
                                if 'caseid_path' not in locals():
                                    caseid_path = default_path + "/" + istartyear + '_' + iendyear + '_' + imake + imodel + '_' + ipdamage
                                    if not os.path.exists(caseid_path):
                                        os.makedirs(caseid_path)
                                    os.chdir(caseid_path)
                                else:
                                    print("Case ID Path already exists")
  
                            else:
                                caseid_path = os.getcwd() + istartyear + '_' + iendyear + '_' + imake + imodel + '_' + ipdamage
                                if not os.path.exists(caseid_path):
                                    os.makedirs(caseid_path)
                                    print("Making direectoyrt")
                                os.chdir(caseid_path)
                                
                            img_num = str(row[0])
                            fileName = caseid_path + '//' + img_num + '.jpg'
                            img.save(fileName)
                            user_in = 'de'
                            break
                        elif 'ne' in user_in.lower():
                            continue
                        elif 'de' in user_in.lower():
                            break
                        elif 'ft' in user_in.lower():
                            image_set = check_image_set(front_images)
                            break
                        elif 'fr' in user_in.lower():
                            image_set = check_image_set(frontright_images)
                            break
                        elif 'ri' in user_in.lower():
                            image_set = check_image_set(right_images)
                            break
                        elif 'br' in user_in.lower():
                            image_set = check_image_set(backright_images) 
                            break
                        elif 'ba' in user_in.lower():
                            image_set = check_image_set(back_images)
                            break
                        elif 'bl' in user_in.lower():
                            image_set = check_image_set(backleft_images)
                            break
                        elif 'le' in user_in.lower():
                            image_set = check_image_set(left_images)
                            break
                        elif 'fl' in user_in.lower():
                            image_set = check_image_set(frontleft_images)
                            break
                        img.close()
                    if 'de' in user_in.lower():
                        break
                    else:
                        continue
                    break      
            if not len(fileName) == 0:
                temp = {'summary':summary}
                temp['caseid'] = extform[n_voi]['caseid']
                temp['casenum'] = page.case['casestr']
                temp['vehnum'] = extform[n_voi]['vehiclenumber']
                temp['year'] = extform[n_voi].modelyear.text
                temp['make'] = extform[n_voi].make.text
                temp['model'] = extform[n_voi].model.text
                temp['curbweight'] = float(extform[n_voi].curbweight.text)
                temp['damloc'] = extform[n_voi].deformationlocation.text
                temp['underride'] = extform[n_voi].overunderride.text
                temp['edr'] = extform[n_voi].edr.text
                #Check correct CDC
                temp['total_dv'] = float(tot)
                temp['long_dv'] = float(lon)
                temp['lateral_dv'] = float(lat)
                temp['smashl'] = float(smash_l)
                temp['crush'] = final_crush
                #Alternate Vehicle Info
                if event['an'].isnumeric():
                    temp['a_vehnum'] = genvehform[n_an]['vehiclenumber']
                    temp['a_year'] = genvehform[n_an].modelyear.text
                    temp['a_make'] = genvehform[n_an].make.text
                    temp['a_model'] = genvehform[n_an].model.text
                    if 'Unk' in genvehform[n_an].curbweight.text:
                        temp['a_curbweight'] = temp['curbweight']
                    else:
                        temp['a_curbweight'] = float(genvehform[n_an].curbweight.text)
                else:
                    temp['a_vehnum'] = event['an']
                    temp['a_year'] = '--'
                    temp['a_make'] = '--'
                    temp['a_model'] = '--'
                    temp['a_curbweight'] = float(99999)
                temp['image'] = img_num
                #temp['a_damloc'] = genvehform[n_an].deformationlocation.text
                contents.append(temp)
                temp = {}
    
#%%
def get_r2(x, y):
    slope, intercept = numpy.polyfit(x, y, 1)
    r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * numpy.var(y, ddof=1)))
    return r_squared
x = []
y_nass = []
y_total = []

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
    e = 0.5992 * numpy.exp(-0.1125 * NASS_vc + 0.003889 * NASS_vc ** 2 - 0.0001153 * NASS_vc ** 3)
    cse['e'] = e
    TOT_dv = NASS_dv*(1.0+e)
    cse['TOT_dv'] = TOT_dv
    x.append(c_bar)
    y_nass.append(NASS_dv)
    y_total.append(TOT_dv)
    #pdb.set_trace()
slope, intercept = numpy.polyfit(x, y_nass, 1)

ind = []
[ind.append(cse['image']) for cse in contents]
df_original = pandas.DataFrame(contents, index = ind)

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
dfn = df.apply(pandas.to_numeric, errors='coerce')

#dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c='r',figsize=(16,12))

fit=numpy.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
fit_e=numpy.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

slope = fit[0]
slope_e = fit_e[0]

intercept = fit[1]
intercept_e = fit_e[1]

s_eq = 'Y = ' + str(round(slope,1)) + 'X + ' + str(round(intercept,1))
s_eq_e = 'Y = ' + str(round(slope_e,1)) + 'X + ' + str(round(intercept_e,1))

# regression lines
plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color='darkblue', linewidth=2)
#plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

predict = numpy.poly1d(fit)
predict_e = numpy.poly1d(fit_e)
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

crush_est = numpy.array([0, 1.0])
print(predict(crush_est))
print(predict_e(crush_est))
print(df)

#%%

# Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
for i in df.index:
    s = 'Caseid: ' + str(df.loc[i].caseid) + '. NASSDV = ' + str(df.loc[i].NASS_dv)
    img = Image.open(caseid_path + '//' + i + '.jpg')
    draw = ImageDraw.Draw(img)
    #draw.text((0, 0),s,(220,20,60),font=font)
    img.show()
    #plt.text(25, 25, s, fontsize=18, bbox=dict(facecolor='white', edgecolor='red', linewidth=2))
    user_in = input(s + ' ' "Select: [SA]ve case, [DE]lete Case, [ST]op: ")
    img.close()
    if 'de' in user_in.lower():
        df = df.drop(index = i)
        df_original = df_original.drop(index = i)
        continue
    elif 'st' in user_in.lower():
        break
    else:
        continue
# Re-Analyze Info - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
dfn = df.apply(pandas.to_numeric, errors='coerce')

#dv_plot_e = dfn.plot.scatter(x="c_bar", y="TOT_dv", c='r',figsize=(16,12))
dv_plot = dfn.plot.scatter(x="c_bar", y="NASS_dv", c='r',figsize=(16,12))

fit=numpy.polyfit(dfn.c_bar, dfn.NASS_dv, 1)
fit_e=numpy.polyfit(dfn.c_bar, dfn.TOT_dv, 1)

slope = fit[0]
slope_e = fit_e[0]

intercept = fit[1]
intercept_e = fit_e[1]

s_eq = 'Y = ' + str(round(slope,1)) + 'X + ' + str(round(intercept,1))
s_eq_e = 'Y = ' + str(round(slope_e,1)) + 'X + ' + str(round(intercept_e,1))

# regression lines
plt.plot(dfn.c_bar, fit[0] * dfn.c_bar + fit[1], color='darkblue', linewidth=2)
#plt.plot(dfn.c_bar, fit_e[0] * dfn.c_bar + fit_e[1], color='red', linewidth=2)

predict = numpy.poly1d(fit)
predict_e = numpy.poly1d(fit_e)
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

crush_est = numpy.array([0, 1.0])
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
#print(csestr)

temp1 = df.sort_values(by=['NASS_dv'])
minval = str(round(temp1.iloc[0]['NASS_dv'],1))
mincase = temp1.iloc[0]['caseid']
maxval = str(round(temp1.iloc[end]['NASS_dv'],1))
maxcase = temp1.iloc[end]['caseid']

dvstr = ' Among these cases, the changes in velocity ranged from as low as ' + minval + ' mph (' + mincase + ') to as high as ' + maxval + ' mph (' + maxcase + ').'

par = csestr + dvstr
writer.writerows([[],[par]])
f.close()

print(par)


