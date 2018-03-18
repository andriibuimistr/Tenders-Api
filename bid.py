# -*- coding: utf-8 -*-
from faker import Faker
import document
from data_for_tender import valueAddedTaxIncluded, tender_currency, above_threshold_active_bid_procurements, below_threshold_procurement
from database import BidsTender, db
import json
import time
from random import randint
import binascii
import os
from tenders.tender_requests import TenderRequests


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


# add bid info to DB (SQLA)
def bid_to_db(bid_id, bid_token, u_identifier, tender_id):
    bid_to_sql = BidsTender(None, bid_id, bid_token, tender_id, None, None, None, None, u_identifier)
    db.session.add(bid_to_sql)
    db.session.commit()
    db.session.remove()
    print 'Add bid to local database'
    return "success"


# create and activate bid for created tender
def run_cycle(bids_quantity, number_of_lots, tender_id, procurement_method, list_of_id_lots, api_version, if_docs):
    tender = TenderRequests(api_version)
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

            attempts = 0
            for every_bid in range(5):
                attempts += 1
                print '{}{}'.format('Publishing bid: Attempt ', attempts)
                created_bid = tender.make_tender_bid(tender_id, bid_json, count)
                if created_bid.status_code == 201:
                    break
                else:
                    continue

            bid_token = created_bid.json()['access']['token']
            bid_id = created_bid.json()['data']['id']

            attempts = 0
            for every_bid in range(5):  # activate bid
                activate_created_bid = tender.activate_tender_bid(tender_id, bid_id, bid_token, activate_bid_body, count)
                time.sleep(0.5)
                if activate_created_bid.status_code == 200:
                    break
                else:
                    attempts += 1
                    print '{}{}'.format('Activating bid: Attempt ', attempts)

            bid_to_db(bid_id, bid_token, identifier, tender_id)  # save bid info to db
            # get_bid_info(bid_location, bid_token, count)  # get info about bid from CDB

            if if_docs == 1:
                print "Add documents to bid"
                document.add_documents_to_bid_ds(tender_id, bid_id, bid_token, procurement_method)
        return bids_json, list_of_bids_json


def make_bid_competitive(list_of_bids, tender_id, api_version, procurement_method):
    tender = TenderRequests(api_version)
    if len(list_of_bids) == 0:
        print 'Bids haven\'t been made!'
    else:
        count = 0
        for bid in range(len(list_of_bids)):
            count += 1
            bid_json = list_of_bids[bid]
            attempts_create = 0
            for x in range(5):
                created_bid = tender.make_tender_bid(tender_id, bid_json, count)
                if created_bid.status_code == 201:
                    break
                else:
                    attempts_create += 1
                    print '{}{}'.format('Publishing bid: Attempt ', attempts_create)
            if procurement_method == 'competitiveDialogueUA':
                activate_bid_body = {"data": {"status": "active"}}
            else:
                activate_bid_body = {"data": {"status": "pending"}}
            bid_token = created_bid.json()['access']['token']
            bid_id = created_bid.json()['data']['id']
            identifier = list_of_bids[bid]['data']['tenderers'][0]['identifier']['id']
            attempts_activate = 0
            for every_bid in range(5):  # activate bid
                activate_created_bid = tender.activate_tender_bid(tender_id, bid_id, bid_token, activate_bid_body, count)
                if activate_created_bid.status_code == 200:
                    break
                else:
                    attempts_activate += 1
                    print '{}{}'.format('Activating bid: Attempt ', attempts_activate)

            bid_to_db(bid_id, bid_token, identifier, tender_id)


def suppliers_for_limited(number_of_lots, tender_id, tender_token, list_of_id_lots, api_version):
    tender = TenderRequests(api_version)
    supplier = 0
    if number_of_lots == 0:
        supplier += 1
        limited_supplier_json = supplier_json_limited()
        tender.add_supplier_limited(tender_id, tender_token, limited_supplier_json, supplier)
    else:
        for lot_id in range(len(list_of_id_lots)):
            supplier += 1
            limited_supplier_json = supplier_json_limited_lots(list_of_id_lots[lot_id])
            tender.add_supplier_limited(tender_id, tender_token, limited_supplier_json, supplier)
