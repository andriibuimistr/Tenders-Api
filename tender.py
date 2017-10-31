# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
import MySQLdb
import requests
import sys

import lots
import variables
from variables import tender_value, tender_guarantee, tender_minimalStep, tender_period, tender_title, \
    tender_description, tender_title_en, tender_description_en, tender_features, procuring_entity, \
    procurementMethodType, mode, submissionMethodDetails, procurementMethodDetails, status, auth_key

'''db = MySQLdb.connect(host="82.163.176.242", user="carrosde_python", passwd="python", db="carrosde_tenders")
# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
cursor = db.cursor()'''

# tender_guarantee_amount = lots.lot_guarantee_amount


def tender_with_lots():
    return u"{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(
        '{"data": {', tender_value, tender_guarantee, tender_minimalStep, tender_title, tender_description,
        tender_title_en, tender_description_en, lots.list_of_lots(), lots.list_of_items_for_lots(), tender_features,
        tender_period, procuring_entity(), procurementMethodType, mode, submissionMethodDetails,
        procurementMethodDetails, status, '}}')


def tender():
    return u"{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(
        '{"data": {', tender_value, tender_guarantee, tender_minimalStep, tender_title, tender_description,
        tender_title_en, tender_description_en, lots.list_of_items_for_tender(), tender_features,
        tender_period, procuring_entity(), procurementMethodType, mode, submissionMethodDetails,
        procurementMethodDetails, status, '}}')

if variables.number_of_lots == 0:
    json_tender = json.loads(tender())
else:
    json_tender = json.loads(tender_with_lots())


host = "https://lb.api-sandbox.openprocurement.org"
api_version = "2.3"


headers = {"Authorization": "Basic {}".format(auth_key),
           "Content-Length": "{}".format(len(json_tender)),
           "Content-Type": "application/json",
           "Host": "lb.api-sandbox.openprocurement.org"}


# Publish tender
def publish_tender():
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('POST',
                         "{}/api/{}/tenders".format(host, api_version),
                         data=json.dumps(json_tender),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Publishing tender:")
        print("       status code:  {}".format(resp.status_code))
        print("       response content:  {}".format(resp.content))
        print("       headers:           {}".format(resp.headers))
        print("       tender id:         {}".format(resp.headers['Location'].split('/')[-1]))
        return resp
    except:
        sys.exit("CDB error")
response = publish_tender()


# Activate tender
def activating_tender():
    activate_tender = json.loads('{ "data": { "status": "active.tendering"}}')
    tender_location = response.headers['Location']
    token = response.json()['access']['token']
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('PATCH',
                         "{}{}{}".format(tender_location, '?acc_token=', token),
                         data=json.dumps(activate_tender),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Activating tender:")
        print("       status code:  {}".format(resp.status_code))
        print("       response content:  {}".format(resp.content))
        print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")
activating_tender = activating_tender()

tender_id_long = response.headers['Location'].split('/')[-1]
tender_token = response.json()['access']['token']
tender_status = activating_tender.json()['data']['status']
tender_id_short = response.json()['data']['tenderID']

'''
# save info to DB
def tender_to_db():
    tender_to_sql = \
        "INSERT INTO tenders VALUES(null, '{}', '{}', '{}', '{}', '{}', null, null, null)".format(
            tender_id_long, response.json()['data']['tenderID'], tender_token, tender_status, variables.number_of_lots)
    cursor.execute(tender_to_sql)
    db.commit()  # you need to call commit() method to save your changes to the database
    db.close()
tender_to_db()'''


# Save id to file
'''def save_report_to_file():
    text_for_file = "{}{}{}{}{}{}{}{}{}{}{}{}{}".format(
        'Tender ID: ', tender_id_long, ', ID: ', tender_id_short, ', response code: ', activating_tender.status_code,
        ', token: ', tender_token, ', published: ', datetime.now(), ', lots: ', variables.number_of_lots, '\n')
    my_file = open('saved_files/reports.txt', 'a+')
    my_file.write(text_for_file)
    my_file.close()
save_report_to_file()'''


def add_tender_to_site():
    print 'Don\'t worry, script is working ...'
    for x in range(5):
        time.sleep(60)
        company_id = 61
        add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
            variables.tender_byustudio_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token,
            '&company=', company_id,'&acc_token=SUPPPER_SEEECRET_STRIIING'))
        add_to_site_response = add_to_site.json()
        if 'tid' in add_to_site_response:
            print 'Tender was added to site'
            tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
            link_to_tender = '{}{}{}{}'.format(
                'Link: ', variables.tender_byustudio_host, '/buyer/tender/view/', add_to_site_response['tid'])
            print tender_id_site
            print link_to_tender

            def save_added_tender_info_to_file():
                text_for_file = "{}{}{}{}{}".format('ID: ', add_to_site_response['tid'], ', ', link_to_tender, '\n')
                my_file = open('saved_files/tender-info-site.txt', 'a+')
                my_file.write(text_for_file)
                my_file.close()
            save_added_tender_info_to_file()
            break
        else:
            print add_to_site_response
            continue
add_tender_to_site()
