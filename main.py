# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from flask import Flask, request, jsonify, send_from_directory, url_for, Response
import demjson
from shutil import copyfile
import os
from datetime import date
from shortuuid import uuid
import tempfile
from myanmartools import ZawgyiDetector
from mmfont.converter import uni512zg1

app = Flask(__name__)

election_title = u"၂၀၂၀ ၿပည္႔ႏွစ္အေထြအေထြ"
gender = "male"
name = u""
race = u""
nric = u""
birthday = u""
father_name = u""
mother_name = u""
address_no = u""
address_is_village = u"no"
address_street_village = u""
address_ward_village = u""
address_township = u""
address_is_state = u"no"
address_state_region = u""

oversea_address_line1 = u""
oversea_address_line2 = u""
oversea_contact_number = u""

date = u""

@app.route('/', methods=['GET', 'POST'])
def form15():
    data = {}
    if request.data:
        data = demjson.decode(request.data)
        # seems like chatfuel checks for the api link without any data
        # this is to check if nric is in the data before processing
        if "nric" in data:
            filename = fill_form(data)
            form_link = url_for('serve_form', filename=filename, _external=True)

            return jsonify({
                'messages':[{
                    'attachment':{
                        'type': 'file',
                        'payload': {'url': form_link}
                    }
                }]
            })
    
    # if there is any problem getting data
    return jsonify({'messages':[
        {'text': 'There is a problem generating a filled form.'},
        {'text': 'Please try again.'}
    ]})

@app.route('/forms/<path:filename>', methods=['GET', 'POST'])
def serve_form(filename):
    return send_from_directory(os.path.join(tempfile.gettempdir(), ''), filename + '.pdf')

def fill_form(data):
    # a unique id for tmp file
    filename = 'ElectionForm15_' + str(uuid()).replace('-', '')

    # make a copy of the file
    copyfile('ElectionForm15.png', os.path.join(tempfile.gettempdir(), filename + '.png'))

    # detect unicode and convert to zawgyi
    detector = ZawgyiDetector()

    for key, value in data.items():
        try:
            score = detector.get_zawgyi_probability(value)
            #print(value, score)
            if 0 < score < 0.8: # not zawgyi, convert it to zawgyi
                data[key] = uni512zg1(value)
        except:
            pass
        
    gender = data.get('gender').strip().lower()
    name = data.get('name').strip()
    race = data.get('race').strip()
    nric = data.get('nric').strip()
    birthday = data.get('birthday').strip()
    father_name = data.get('father_name').strip()
    mother_name = data.get('mother_name').strip()
    address_no = data.get('address_no').strip()
    address_is_village = data.get('address_is_village').strip().lower()
    address_street_village = data.get('address_street_village').strip()
    address_ward_village = data.get('address_ward_village').strip()
    address_township = data.get('address_township').strip()
    address_is_state = data.get('address_is_state').strip().lower()
    address_state_region = data.get('address_state_region').strip()
    oversea_address_line1 = data.get('oversea_address_line1').strip()
    oversea_address_line2 = data.get('oversea_address_line2').strip()
    oversea_contact_number = data.get('oversea_contact_number').strip()
    date = data.get('date').strip()

    with Image.open(os.path.join(tempfile.gettempdir(), filename + '.png')) as im:
        draw = ImageDraw.Draw(im)

        font = ImageFont.truetype('ZawgyiOne.ttf', 36)

        # election region
        if address_is_state == 'yes':
            election_region = address_state_region + u" ျပည္နယ္၊ " + address_township
        else:
            election_region = address_state_region + u" တိုင္းေဒသႀကီး၊ " + address_township
            
        draw.text((400,790), election_region, 'blue', font=font)

        # name
        draw.text((870, 875), name, 'blue', font=font)

        # election title
        draw.text((1700, 875), election_title, 'blue', font=font)

        # particulars
        draw.text((1150, 1300), name, 'blue', font=font)
        draw.text((1150, 1380), race, 'blue', font=font)
        draw.text((1150, 1460), nric, 'blue', font=font)
        draw.text((1150, 1540), birthday, 'blue', font=font)
        draw.text((1150, 1630), father_name, 'blue', font=font)
        draw.text((1150, 1720), mother_name, 'blue', font=font)

        # address
        draw.text((1680, 1860), address_no, 'blue', font=font)
        draw.text((580, 1930), address_street_village, 'blue', font=font)
        draw.text((1230, 1930), address_ward_village, 'blue', font=font)
        draw.text((580, 2015), address_township, 'blue', font=font)
        draw.text((1140, 2015), address_state_region, 'blue', font=font)

        # oversea address
        draw.text((1430, 2400), oversea_address_line1, 'blue', font=font)
        draw.text((1430, 2485), oversea_address_line2 + u" PH: " + oversea_contact_number, 'blue', font=font)

        # date
        draw.text((520, 3000), date, 'blue', font=font)

        # strike throughs gender
        if gender == 'male':
            draw.line([(705,920), (816, 920)], 'blue', 8)
            draw.line([(890,1080), (1008, 1080)], 'blue', 8)
            draw.line([(590,1160), (700, 1160)], 'blue', 8)
        else:
            draw.line([(480,920), (660, 920)], 'blue', 8)
            draw.line([(620,1080), (810, 1080)], 'blue', 8)
            draw.line([(330,1160), (530, 1160)], 'blue', 8)

        # strike throughs village
        if address_is_village == 'yes':
            draw.line([(930,1980), (1025, 1980)], 'blue', 8)
            draw.line([(1640,1980), (1800, 1980)], 'blue', 8)
        else:
            draw.line([(1053,1980), (1200, 1980)], 'blue', 8)
            draw.line([(1840,1980), (2100, 1980)], 'blue', 8)    
        
        # strike throughs state
        if address_is_state == 'yes':
            draw.line([(1630,2060), (1900, 2060)], 'blue', 8)
        else:
            draw.line([(1940,2060), (2100, 2060)], 'blue', 8)

        if im.mode == 'RGBA':
            im = im.convert('RGB')
        try:
            os.remove(os.path.join(tempfile.gettempdir(), filename + '.png'))
        except:
            pass

        im.save(os.path.join(tempfile.gettempdir(), filename + '.pdf'))

        return filename



if __name__ == '__main__':
    app.run()

'''
gender = "male"
name = u"ဦးတင္ခိုင္"
race = u"ဗမာ"
nric = u"၁၂ / အစန( ႏိုင္) ၀၈၀၀၈၅"
birthday = u"၁၂ - ၁၀ - ၁၉၅၇"
father_name = u"ဦးေရႊတင္"
mother_name = u" ေဒၚၿမႀကင္"
address_no = u"၃၁၂"
address_is_village = "no"
address_street_village = u"က - ၅"
address_ward_village = u"ၿမိဳ႔သစ္"
address_township = u"အင္းစိန္"
address_is_state = "no"
address_state_region = u"ရန္ကုန္"
oversea_address_line1 = u"BLK 351, Clementi Ave 2, #09-51"
oversea_address_line2 = u"Singapore, 120351"
oversea_contact_number = u"+65 6929 3435"
date = u"၁၇ - ၀၇ - ၂၀၂၀"




{
"gender":"male",
"name":"ဦးတင္ခိုင္",
"race":"ဗမာ",
"nric":"၁၂ / အစန( ႏိုင္) ၀၈၀၀၈၅",
"birthday":"၁၂ - ၁၀ - ၁၉၅၇",
"father_name":"ဦးေရႊတင္",
"mother_name":" ေဒၚၿမႀကင္",
"address_no":"၃၁၂",
"address_is_village":"no",
"address_street_village":"က - ၅",
"address_ward_village":"ၿမိဳ႔သစ္",
"address_township":"အင္းစိန္",
"address_is_state":"no",
"address_state_region":"ရန္ကုန္",
"oversea_address_line1":"BLK 351, Clementi Ave 2, #09-51",
"oversea_address_line2":"Singapore, 120351",
"oversea_contact_number":"+65 6929 3435",
"date":"၁၇ - ၀၇ - ၂၀၂၀"
မ ှတ္ပုံတင္အမှတ္
}
'''
