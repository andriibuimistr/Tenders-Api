# -*- coding: utf-8 -*-
import tender
import sys
import requests
from variables import host, api_version, auth_key, number_of_lots, procurement_method, valueAddedTaxIncluded,\
    tender_currency, above_threshold_procurement_for_bid
from lots import list_of_id
import json
import MySQLdb
import time
from random import randint
# DB connections
'''db = MySQLdb.connect(host="82.163.176.242", user="carrosde_python", passwd="python", db="carrosde_tenders")
# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
cursor = db.cursor()'''

tender_id = tender.tender_id_long  # get tender_id from tender file


# number of bids
def number_of_bids():
    number_of_bids_input = (raw_input('Количество ставок (от 1 до 10, 0 - не делать ставки)')).decode('utf-8')
    while number_of_bids_input.isdigit() is not True or int(number_of_bids_input) > 10:
        number_of_bids_input = raw_input(
            'Введите правильное значение :) (от 1 до 10, 0 - не делать ставки)').decode('utf-8')
    else:
        number_of_bids_input = int(number_of_bids_input)
    return number_of_bids_input
number_of_bids = number_of_bids()


# generate value for lots
def lot_values_bid_generator():
    list_of_lots_in_bid = []
    for lot in range(number_of_lots):
        lot_id = list_of_id[lot]
        #if procurement_method in above_threshold_procurement_for_bid:
        related_lot_value = json.loads(
            '{}{}{}{}{}{}{}{}{}'.format('{"relatedLot": "', lot_id, '", "value": {"amount": ', randint(100, 999),
                                        ', "valueAddedTaxIncluded": ', valueAddedTaxIncluded, ', "currency": ',
                                        tender_currency, '}}'))
        '''else:
            related_lot_value = json.loads('{}{}{}{}{}'.format(
                '{"relatedLot": "', lot_id, '", "value": {"amount": ', randint(100, 999), '}}'))'''
        list_of_lots_in_bid.append(related_lot_value)
    bid_value = json.dumps(list_of_lots_in_bid)
    return '{}'.format(bid_value)


# generate value for tender
def values_bid_generator():
        tender_bid_value = json.loads(
            '{}{}{}{}{}{}{}'.format('{"amount": ', randint(100, 999), ', "currency": ', tender_currency,
                                    ', "valueAddedTaxIncluded": ', valueAddedTaxIncluded, '}'))
        return tender_bid_value


# generate json for bid (tender with lots)
def bid_json_open_procedure_lots():
    bid_lot_value = lot_values_bid_generator()
    bid_json_open_body = {"data": {
                            "selfEligible": True,
                            "selfQualified": True,
                            "tenderers": [
                              {
                                "contactPoint": {
                                  "telephone": "+380 (432) 21-69-30",
                                  "name": "Сергій Олексюк",
                                  "email": "bidder@r.com"
                                },
                                "identifier": {
                                  "scheme": "UA-EDR",
                                  "id": randint(1000000000, 9999999999),
                                  "uri": "http://www.site.domain"
                                },
                                "name": "ДКП «Школяр»",
                                "address": {
                                  "countryName": "Україна",
                                  "postalCode": "21100",
                                  "region": "м. Вінниця",
                                  "streetAddress": "вул. Островського, 33",
                                  "locality": "м. Вінниця"
                                }
                              }
                            ],
                            "subcontractingDetails": "ДКП «Книга», Україна, м. Львів, вул. Островського, 33",
                            "lotValues": json.loads(bid_lot_value)
                            }
                            }
    return bid_json_open_body


# generate json for bid (simple tender)
def bid_json_open_procedure():
    tender_value = values_bid_generator()
    bid_json_open_body = {"data": {
                            "selfEligible": True,
                            "selfQualified": True,
                            "tenderers": [
                              {
                                "contactPoint": {
                                  "telephone": "+380 (432) 21-69-30",
                                  "name": "Сергій Олексюк",
                                  "email": "bidder@r.com"
                                },
                                "identifier": {
                                  "scheme": "UA-EDR",
                                  "id": randint(1000000000, 9999999999),
                                  "uri": "http://www.site.domain"
                                },
                                "name": "ДКП «Школяр»",
                                "address": {
                                  "countryName": "Україна",
                                  "postalCode": "21100",
                                  "region": "м. Вінниця",
                                  "streetAddress": "вул. Островського, 33",
                                  "locality": "м. Вінниця"
                                }
                              }
                            ],
                            "value": tender_value,
                            "subcontractingDetails": "ДКП «Книга», Україна, м. Львів, вул. Островського, 33"
                            }
                            }
    return bid_json_open_body
# ----------------------------------------

if number_of_lots == 0:
    bid_json_open_length = bid_json_open_procedure()
else:
    bid_json_open_length = bid_json_open_procedure_lots()

# select status for activate bid
if procurement_method in above_threshold_procurement_for_bid:
    activate_bid_body = {"data": {"status": "active"}}
else:
    activate_bid_body = {"data": {"status": "pending"}}

headers = {"Authorization": "Basic {}".format(auth_key),
           "Content-Length": "{}".format(len(bid_json_open_length)),
           "Content-Type": "application/json",
           "Host": "lb.api-sandbox.openprocurement.org"}


def create_bid_openua_procedure(n_bid):
    s = requests.Session()
    s.request('GET', '{}/api/{}/tenders'.format(host, api_version))
    if number_of_lots == 0:
        bid_json = bid_json_open_procedure()
    else:
        bid_json = bid_json_open_procedure_lots()
    r = requests.Request('POST',
                         '{}/api/{}/tenders/{}/bids'.format(host, api_version, tender_id),
                         data=json.dumps(bid_json),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}:'.format('Publishing bid ', n_bid))
        print("       status code:  {}".format(resp.status_code))
        print("       response content:  {}".format(resp.content))
        print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")


def activate_bid(bid_location, bid_token, n_bid):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('PATCH',
                         "{}{}{}".format(bid_location, '?acc_token=', bid_token),
                         data=json.dumps(activate_bid_body),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}:'.format('Activating bid ', n_bid))
        print("       status code:  {}".format(resp.status_code))
        print("       response content:  {}".format(resp.content))
        print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")


def get_bid_info(bid_location, bid_token, n_bid):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('GET',
                         "{}{}{}".format(bid_location, '?acc_token=', bid_token),
                         headers={"Authorization": "Basic " + auth_key},
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    prepped = s.prepare_request(r)
    resp = s.send(prepped)
    print('{}{}:'.format('Getting info bid ', n_bid))
    print("       status code:  {}".format(resp.status_code))
    print("       response content:  {}".format(resp.content))
    print("       headers:           {}".format(resp.headers))
    return resp


'''def bid_to_db(bid_id, bid_token):
    bid_to_sql = \
        "INSERT INTO bids VALUES(null, '{}', '{}', '{}', null, null, null, null)".format(bid_id, bid_token, tender_id)
    cursor.execute(bid_to_sql)'''


def run_cycle(bids_quantity):
    if bids_quantity == 0:
        print 'Ставки не были сделаны!'
    else:
        count = 0
        for x in range(bids_quantity):
            count += 1
            created_bid = create_bid_openua_procedure(count)  # create bid
            bid_location = created_bid.headers['Location']
            bid_token = created_bid.json()['access']['token']
            bid_id = created_bid.json()['data']['id']
            time.sleep(0.5)
            for every_bid in range(5):
                bid_activation_status = activate_bid(bid_location, bid_token, count)
                if bid_activation_status.status_code == 200:
                    break
                else:
                    activate_bid(bid_location, bid_token, count)

            '''bid_to_db(bid_id, bid_token)  # write bid info to db
            # get_bid_info(bid_location, bid_token, count)
    db.commit()  # you need to call commit() method to save your changes to the database
    db.close()'''
run_cycle(number_of_bids)
