# -*- coding: utf-8 -*-
from faker import Faker
import requests
import document
from data_for_tender import auth_key, valueAddedTaxIncluded, tender_currency, above_threshold_active_bid_procurements, below_threshold_procurement
from database import BidsTender, db
import json
import time
from random import randint
import binascii
import os
from flask import abort
from requests.exceptions import ConnectionError


fake = Faker('uk_UA')


# generate value for lots
def lot_values_bid_generator(number_of_lots, list_of_id_lots):
    list_of_lots_in_bid = []
    for lot in range(number_of_lots):
        lot_id = list_of_id_lots[lot]
        related_lot_value = json.loads(
            '{}'.format(json.dumps({"relatedLot": lot_id,
                                    "value": {"amount": randint(100, 999),
                                              "valueAddedTaxIncluded": valueAddedTaxIncluded,
                                              "currency": tender_currency}
                                    })))
        list_of_lots_in_bid.append(related_lot_value)
    bid_value = json.dumps(list_of_lots_in_bid)
    return '{}'.format(bid_value)


# generate value for tender
def values_bid_generator_above():
        tender_bid_value = json.loads(
            '{}'.format(json.dumps({"amount": randint(100, 999),
                                    "currency": tender_currency,
                                    "valueAddedTaxIncluded": valueAddedTaxIncluded
                                    })))
        return tender_bid_value


def supplier_json_limited():
    tender_value = values_bid_generator_above()
    suppliers_json_limited = {"data": {
                                    "date": "2016-01-14T18:07:00.628073+02:00",
                                    "status": "pending",
                                    "suppliers": [
                                      {
                                        "contactPoint": {
                                          "telephone": "+380 (432) 21-69-30",
                                          "name": "Сергій Олексюк",
                                          "email": "soleksuk@gmail.com"
                                        },
                                        "identifier": {
                                          "scheme": "UA-EDR",
                                          "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                                          "id": "00037256",
                                          "uri": "http://sch10.edu.vn.ua/"
                                        },
                                        "name": fake.company(),
                                        "address": {
                                          "countryName": "Україна",
                                          "postalCode": "21100",
                                          "region": "м. Вінниця",
                                          "streetAddress": "вул. Островського, 33",
                                          "locality": "м. Вінниця"
                                        }
                                      }
                                    ],
                                    "id": (binascii.hexlify(os.urandom(16))),
                                    "value": tender_value
                                  }
                              }
    return suppliers_json_limited


def supplier_json_limited_lots(lot_id):
    tender_value = values_bid_generator_above()
    suppliers_json_limited = {"data": {
                                    "date": "2016-01-14T18:07:00.628073+02:00",
                                    "status": "pending",
                                    "suppliers": [
                                      {
                                        "contactPoint": {
                                          "telephone": "+380 (432) 21-69-30",
                                          "name": "Сергій Олексюк",
                                          "email": "soleksuk@gmail.com"
                                        },
                                        "identifier": {
                                          "scheme": "UA-EDR",
                                          "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                                          "id": "00037256",
                                          "uri": "http://sch10.edu.vn.ua/"
                                        },
                                        "name": fake.company(),
                                        "address": {
                                          "countryName": "Україна",
                                          "postalCode": "21100",
                                          "region": "м. Вінниця",
                                          "streetAddress": "вул. Островського, 33",
                                          "locality": "м. Вінниця"
                                        }
                                      }
                                    ],
                                    "id": (binascii.hexlify(os.urandom(16))),
                                    "value": tender_value,
                                    "lotID": lot_id
                                  }
                              }
    return suppliers_json_limited


def add_supplier_limited(tender_id, tender_token, headers, host_kit, limited_supplier_json, supplier_number):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request('GET', '{}/api/{}/tenders'.format(host_kit[0], host_kit[1]))
            r = requests.Request('POST', '{}/api/{}/tenders/{}/awards?acc_token={}'.format(host_kit[0], host_kit[1], tender_id, tender_token),
                                 data=json.dumps(limited_supplier_json),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            resp.raise_for_status()
            if resp.status_code == 201:
                print('{}{}: {}'.format('Add supplier ', supplier_number, 'Success'))
                print("       status code:  {}".format(resp.status_code))
                return 0, resp, resp.content, resp.status_code
            else:
                print('{}{}: {}'.format('Add supplier ', supplier_number, 'Error'))
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                time.sleep(1)
                if attempts >= 5:
                    abort(resp.status_code, 'Add supplier error ' + resp.content)
        except ConnectionError as e:
            print 'CDB Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Add supplier error: ' + str(e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Add supplier error: ' + str(e))


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
                                "name": fake.company(),
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
    tender_value = values_bid_generator_above()
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
                                "name": fake.company(),
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


# generate values for simple esco bid
def values_bid_generator_esco():
    annual_costs_reduction_list = []
    cost = 0
    for x in range(21):
        cost += 1000
        if cost > 15000:
            cost = 15000
        annual_costs_reduction_list.append(cost)
    return annual_costs_reduction_list


# # generate values for multilot esco bid
def lot_values_bid_generator_esco(number_of_lots, list_of_id_lots):
    list_of_lots_in_bid = []
    tender_value = values_bid_generator_esco()
    for lot in range(number_of_lots):
        lot_id = list_of_id_lots[lot]
        related_lot_value = {"relatedLot": lot_id,
                             "value": {
                                  "contractDuration": {
                                    "days": 0,
                                    "years": 15
                                  },
                                  "yearlyPaymentsPercentage": 0.8,
                                  "annualCostsReduction": tender_value
                                }}
        list_of_lots_in_bid.append(related_lot_value)
    bid_value = json.dumps(list_of_lots_in_bid)
    return '{}'.format(bid_value)


# generate json for bid (tender with lots)
def bid_json_esco_lots(user_idf, number_of_lots, list_of_id_lots):
    bid_lot_value = lot_values_bid_generator_esco(number_of_lots, list_of_id_lots)
    bid_json_esco_body = {"data": {
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
                                "name": fake.company(),
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
    return bid_json_esco_body


# generate json for bid (simple tender)
def bid_json_esco_simple(user_idf):
    tender_value = values_bid_generator_esco()
    bid_json_esco_body = {"data": {
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
                                "name": fake.company(),
                                "address": {
                                  "countryName": "Україна",
                                  "postalCode": "21100",
                                  "region": "м. Вінниця",
                                  "streetAddress": "вул. Островського, 33",
                                  "locality": "м. Вінниця"
                                }
                              }
                            ],
                            "value": {
                                  "contractDuration": {
                                    "days": 74,
                                    "years": 10
                                  },
                                  "yearlyPaymentsPercentage": 0.8,
                                  "annualCostsReduction": tender_value
                                },
                            "subcontractingDetails": "ДКП «Книга», Україна, м. Львів, вул. Островського, 33"
                            }
                          }
    return bid_json_esco_body


# select correct json for bid using procurement method
def determine_procedure_for_bid(procurement_method):
    if procurement_method in above_threshold_active_bid_procurements + below_threshold_procurement:
        activate_bid_body = {"data": {"status": "active"}}
    else:
        activate_bid_body = {"data": {"status": "pending"}}
    return activate_bid_body


#  generate headers for bid request
def headers_bid(bid_json_open_length, headers_host):
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(bid_json_open_length))),
               "Content-Type": "application/json",
               "Host": headers_host}
    return headers


# create bid in CDB
def create_bid_openua_procedure(n_bid, tender_id, bid_json, headers, host, api_version):
    try:
        s = requests.Session()
        s.request('GET', '{}/api/{}/tenders'.format(host, api_version))
        r = requests.Request('POST', '{}/api/{}/tenders/{}/bids'.format(host, api_version, tender_id),
                             data=json.dumps(bid_json),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        resp.raise_for_status()
        if resp.status_code == 201:
            print('{}{}: {}'.format('Publishing bid ', n_bid, 'Success'))
            print("       status code:  {}".format(resp.status_code))
        else:
            print('{}{}: {}'.format('Publishing bid ', n_bid, 'Error'))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        bid_location = resp.headers['Location']  # get url of created bid
        bid_token = resp.json()['access']['token']  # get token of created bid
        bid_id = resp.json()['data']['id']  # get id of created bid
        return 0, resp.status_code, bid_location, bid_token, bid_id
    except Exception as e:
        return 1, e


# activate created bid
def activate_bid(bid_location, bid_token, n_bid, headers, activate_bid_body, host, api_version):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH',
                             "{}{}{}".format(bid_location, '?acc_token=', bid_token),
                             data=json.dumps(activate_bid_body),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        resp.raise_for_status()
        if resp.status_code == 200:
            print('{}{}: {}'.format('Activating bid ', n_bid,  'Success'))
            print("       status code:  {}".format(resp.status_code))
        else:
            print('{}{}: {}'.format('Activating bid ', n_bid,  'Error'))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return 0, resp.status_code
    except Exception as e:
        return 1, e


# get info about bid
'''def get_bid_info(bid_location, bid_token, n_bid):
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
        sys.exit("CDB error")'''


# DB connections

# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")


# add bid info to DB (SQLA)
def bid_to_db(bid_id, bid_token, u_identifier, tender_id):
    bid_to_sql = BidsTender(None, bid_id, bid_token, tender_id, None, None, None, None, u_identifier)
    db.session.add(bid_to_sql)
    db.session.commit()  # you need to call commit() method to save your changes to the database
    print 'Add bid to local database'
    return "success"


# create and activate bid for created tender
def run_cycle(bids_quantity, number_of_lots, tender_id, procurement_method, list_of_id_lots, host_kit, if_docs):
    activate_bid_body = determine_procedure_for_bid(procurement_method)
    bids_json = []
    if bids_quantity == 0:
        print 'Bids haven\'t been made!'
        return {"description": "tender was created without bids"}
    else:
        count = 0
        list_of_bids_json = []
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
            if number_of_lots == 0:  # select json for bid
                if procurement_method == 'esco':
                    bid_json = bid_json_esco_simple(identifier)
                else:
                    bid_json = bid_json_open_procedure(identifier)
            else:
                if procurement_method == 'esco':
                    bid_json = bid_json_esco_lots(identifier, number_of_lots, list_of_id_lots)
                else:
                    bid_json = bid_json_open_procedure_lots(identifier, number_of_lots, list_of_id_lots)

            if procurement_method == 'belowThreshold':
                del bid_json["data"]["selfEligible"], bid_json["data"]["selfQualified"], bid_json["data"]["subcontractingDetails"]
            list_of_bids_json.append(bid_json)

            headers = headers_bid(bid_json, host_kit[3])  # generate headers for bid

            attempts = 0
            for every_bid in range(5):
                attempts += 1
                print '{}{}'.format('Publishing bid: Attempt ', attempts)
                created_bid = create_bid_openua_procedure(count, tender_id, bid_json, headers, host_kit[0], host_kit[1])  # create bid
                if created_bid[1] == 201:
                    break
                else:
                    continue

            if created_bid[0] == 1:
                print created_bid[1]
                bids_json.append({"bid_number": count,
                                  "create_bid_status_code": 500,
                                  "description": str(created_bid[1])
                                  })
            else:
                bid_location = created_bid[2]
                bid_token = created_bid[3]
                bid_id = created_bid[4]

                attempts = 0
                for every_bid in range(5):  # activate bid
                    activate_created_bid = activate_bid(bid_location, bid_token, count, headers, activate_bid_body, host_kit[0], host_kit[1])
                    time.sleep(0.5)
                    if activate_created_bid[1] == 200:
                        break
                    else:
                        attempts += 1
                        print '{}{}'.format('Activating bid: Attempt ', attempts)

                add_bid_db = bid_to_db(bid_id, bid_token, identifier, tender_id)  # save bid info to db
                # get_bid_info(bid_location, bid_token, count)  # get info about bid from CDB

                if if_docs == 1:
                    print "Add documents to bid"
                    added_to_bid_documents = document.add_documents_to_bid_ds(tender_id, bid_id, bid_token, procurement_method)
                else:
                    added_to_bid_documents = "This bid has no documents"

                bids_json.append({"bid_id": bid_id,
                                  "create_bid_status_code": created_bid[1],
                                  # activate_bid_key: activate_created_bid_result,
                                  "add_bid_to_db_status": add_bid_db,
                                  "documents_of_bid": added_to_bid_documents
                                  })
        return bids_json, list_of_bids_json


def make_bid_competitive(list_of_bids, tender_id, headers, host_kit, procurement_method):
    if len(list_of_bids) == 0:
        print 'Bids haven\'t been made!'
    else:
        count = 0
        for bid in range(len(list_of_bids)):
            count += 1
            bid_json = list_of_bids[bid]
            attempts_create = 0
            for x in range(5):
                created_bid = create_bid_openua_procedure(count, tender_id, bid_json, headers, host_kit[0], host_kit[1])
                if created_bid[1] == 201:
                    break
                else:
                    attempts_create += 1
                    print '{}{}'.format('Publishing bid: Attempt ', attempts_create)
            if procurement_method == 'competitiveDialogueUA':
                activate_bid_body = {"data": {"status": "active"}}
            else:
                activate_bid_body = {"data": {"status": "pending"}}
            bid_location = created_bid[2]
            bid_token = created_bid[3]
            bid_id = created_bid[4]
            identifier = list_of_bids[bid]['data']['tenderers'][0]['identifier']['id']
            attempts_activate = 0
            for every_bid in range(5):  # activate bid
                activate_created_bid = activate_bid(bid_location, bid_token, count, headers, activate_bid_body, host_kit[0], host_kit[1])
                if activate_created_bid[1] == 200:
                    break
                else:
                    attempts_activate += 1
                    print '{}{}'.format('Activating bid: Attempt ', attempts_activate)

            add_bid_2nd_stage_db = bid_to_db(bid_id, bid_token, identifier, tender_id)


def suppliers_for_limited(number_of_lots, tender_id, tender_token, headers, procurement_method, list_of_id_lots, host_kit):
    supplier = 0
    if number_of_lots == 0:
        supplier += 1
        limited_supplier_json = supplier_json_limited()
        add_supplier_limited(tender_id, tender_token, headers, host_kit, limited_supplier_json, supplier)
    else:
        for lot_id in range(len(list_of_id_lots)):
            supplier += 1
            limited_supplier_json = supplier_json_limited_lots(list_of_id_lots[lot_id])
            add_supplier_limited(tender_id, tender_token, headers, host_kit, limited_supplier_json, supplier)






