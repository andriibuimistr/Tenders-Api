# -*- coding: utf-8 -*-
import sys
import requests
from variables import host, api_version, auth_key, valueAddedTaxIncluded, tender_currency,\
    above_threshold_active_bid_procurements
import json
import MySQLdb
import time
import variables
from random import randint


# number of bids input
def number_of_bids():
    number_of_bids_input = (raw_input('Количество ставок (от 1 до 10, 0 - не делать ставки)')).decode('utf-8')
    while number_of_bids_input.isdigit() is not True or int(number_of_bids_input) > 10:
        number_of_bids_input = raw_input(
            'Введите правильное значение :) (от 1 до 10, 0 - не делать ставки)').decode('utf-8')
    else:
        number_of_bids_input = int(number_of_bids_input)
    return number_of_bids_input


# generate value for lots
def lot_values_bid_generator(number_of_lots, list_of_id_lots):
    list_of_lots_in_bid = []
    for lot in range(number_of_lots):
        lot_id = list_of_id_lots[lot]
        related_lot_value = json.loads(
            '{}{}{}{}{}{}{}{}{}'.format('{"relatedLot": "', lot_id, '", "value": {"amount": ', randint(100, 999),
                                        ', "valueAddedTaxIncluded": ', valueAddedTaxIncluded, ', "currency": ',
                                        tender_currency, '}}'))
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
def bid_json_open_procedure_lots(user_idf, number_of_lots, list_of_id_lots):
    bid_lot_value = lot_values_bid_generator(number_of_lots, list_of_id_lots)
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
                                  "id": user_idf,
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
def bid_json_open_procedure(user_idf):
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
                                  "id": user_idf,
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


# select correct json for bid using procurement method
def determine_procedure_for_bid(procurement_method):
    if procurement_method in above_threshold_active_bid_procurements:
        activate_bid_body = {"data": {"status": "active"}}
    else:
        activate_bid_body = {"data": {"status": "pending"}}
    return activate_bid_body


#  generate headers for bid request
def headers_bid(bid_json_open_length):
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(bid_json_open_length))),
               "Content-Type": "application/json",
               "Host": "lb.api-sandbox.openprocurement.org"}
    return headers


# create bid in CDB
def create_bid_openua_procedure(n_bid, tender_id, bid_json, headers):
    s = requests.Session()
    s.request('GET', '{}/api/{}/tenders'.format(host, api_version))
    r = requests.Request('POST',
                         '{}/api/{}/tenders/{}/bids'.format(host, api_version, tender_id),
                         data=json.dumps(bid_json),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 201:
            print('{}{}: {}'.format('Publishing bid ', n_bid, 'Success'))
            print("       status code:  {}".format(resp.status_code))
        else:
            print('{}{}: {}'.format('Publishing bid ', n_bid, 'Error'))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")


# activate created bid
def activate_bid(bid_location, bid_token, n_bid, headers, activate_bid_body):
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
        if resp.status_code == 200:
            print('{}{}: {}'.format('Activating bid ', n_bid,  'Success'))
            print("       status code:  {}".format(resp.status_code))
        else:
            print('{}{}: {}'.format('Activating bid ', n_bid,  'Error'))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")


# get info about bid
def get_bid_info(bid_location, bid_token, n_bid):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('GET',
                         "{}{}{}".format(bid_location, '?acc_token=', bid_token),
                         headers={"Authorization": "Basic " + auth_key},
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print('{}{}: {}'.format('Getting info bid ', n_bid, 'Success'))
            print("       status code:  {}".format(resp.status_code))
        else:
            print('{}{}: {}'.format('Getting info bid ', n_bid, 'Error'))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return resp
    except:
        sys.exit("CDB error")


# DB connections

# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")


# add bid info to DB
def bid_to_db(bid_id, bid_token, u_identifier, tender_id):
    print 'Add bid to local database'
    db = variables.database()
    cursor = db.cursor()
    bid_to_sql = \
        "INSERT INTO bids VALUES(null, '{}', '{}', '{}', null, null, null, null, '{}')".format(
            bid_id, bid_token, tender_id, u_identifier)
    cursor.execute(bid_to_sql)
    db.commit()  # you need to call commit() method to save your changes to the database
    db.close()


# create and activate bid for created tender
def run_cycle(bids_quantity, number_of_lots, tender_id, procurement_method, list_of_id_lots):
    activate_bid_body = determine_procedure_for_bid(procurement_method)
    if bids_quantity == 0:
        print 'Ставки не были сделаны!'
    else:
        count = 0
        for x in range(bids_quantity):
            count += 1
            identifier_list = ['00037256', '14360570', '01202000']  # list of user identifiers from site
            if bids_quantity < 4:
                identifier_list = identifier_list
                identifier = identifier_list[x]
            else:
                for uid in range(bids_quantity - 3):
                    identifier_list.append(randint(10000000, 99999999))  # random user identifier
                identifier = identifier_list[x]
            if number_of_lots == 0:
                bid_json = bid_json_open_procedure(identifier)
            else:
                bid_json = bid_json_open_procedure_lots(identifier, number_of_lots, list_of_id_lots)
            headers = headers_bid(bid_json)  # generate headers for bid
            created_bid = create_bid_openua_procedure(count, tender_id, bid_json, headers)  # create bid
            bid_location = created_bid.headers['Location']  # get url of created bid
            bid_token = created_bid.json()['access']['token']  # get token of created bid
            bid_id = created_bid.json()['data']['id']  # get id of created bid
            time.sleep(0.5)
            for every_bid in range(5):  # activate bid
                bid_activation_status = activate_bid(bid_location, bid_token, count, headers, activate_bid_body)
                if bid_activation_status.status_code == 200:
                    break
                else:
                    activate_bid(bid_location, bid_token, count, headers, activate_bid_body)
            bid_to_db(bid_id, bid_token, identifier, tender_id)  # save bid info to db
            # get_bid_info(bid_location, bid_token, count)  # get info about bid from CDB
