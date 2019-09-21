# -*- coding: utf-8 -*-
from faker import Faker
import document
from tenders.tender_additional_data import below_threshold_procurement, above_threshold_active_bid_procurements, limited_procurement
from database import BidsTender, db
from random import randint
from cdb_requests import TenderRequests


fake = Faker('uk_UA')


# select correct json for bid using procurement method
def determine_procedure_for_bid(procurement_method):
    if procurement_method in above_threshold_active_bid_procurements + below_threshold_procurement:
        activate_bid_body = {"data": {"status": "active"}}
    else:
        activate_bid_body = {"data": {"status": "pending"}}
    return activate_bid_body


# add bid info to DB (SQLA)
def bid_to_db(bid_id, bid_token, u_identifier, tender_id):
    bid_to_sql = BidsTender(None, bid_id, bid_token, tender_id, None, None, None, None, u_identifier)
    db.session.add(bid_to_sql)
    db.session.commit()
    db.session.remove()
    print('Add bid to local database')
    return "success"


def generate_annual_costs_reduction_list():
    annual_costs_reduction_list = []
    cost = 0
    for x in range(21):
        cost += 1000
        if cost > 15000:
            cost = 15000
        annual_costs_reduction_list.append(cost)
    return annual_costs_reduction_list


def generate_bid_values(tender_json, lot_number):
    list_of_lots_id = []
    procurement_method = tender_json['data']['procurementMethodType']
    if 'lots' in tender_json['data']:
        number_of_lots = len(tender_json['data']['lots'])
        list_of_lots_id = []
        for lot in range(number_of_lots):
            list_of_lots_id.append(tender_json['data']['lots'][lot]['id'])
    else:
        number_of_lots = 0

    if procurement_method != 'esco':
        tender_currency = tender_json['data']['value']['currency']
        value_added_tax_included = tender_json['data']['value']['valueAddedTaxIncluded']
        if number_of_lots == 0:
            values_json = {"value": {
                            "amount": randint(100, 999),
                            "currency": tender_currency,
                            "valueAddedTaxIncluded": value_added_tax_included
                     }}
        else:
            values_json = {"lotValues": []}
            for lot in range(number_of_lots):
                lot_id = list_of_lots_id[lot]
                values = {
                            "relatedLot": lot_id,
                            "value": {
                                    "amount": randint(100, 999),
                                    "valueAddedTaxIncluded": value_added_tax_included,
                                    "currency": tender_currency
                            }
                        }
                if procurement_method in limited_procurement:
                    values_json = values
                    values_json['lotID'] = list_of_lots_id[lot_number]
                    del values_json['relatedLot']
                else:
                    values_json['lotValues'].append(values)
    else:
        if number_of_lots == 0:
            values_json = {"value": {
                                  "contractDuration": {
                                    "days": 0,
                                    "years": 15
                                  },
                                  "yearlyPaymentsPercentage": 0.8,
                                  "annualCostsReduction": generate_annual_costs_reduction_list()
                                }}
        else:
            values_json = {"lotValues": []}
            for lot in range(number_of_lots):
                lot_id = list_of_lots_id[lot]
                values = {"relatedLot": lot_id,
                          "value": {
                                  "contractDuration": {
                                    "days": 0,
                                    "years": 15
                                  },
                                  "yearlyPaymentsPercentage": 0.8,
                                  "annualCostsReduction": generate_annual_costs_reduction_list()
                                }}
                values_json['lotValues'].append(values)

    if 'features' in tender_json['data']:
        values_json['parameters'] = []
        for feature in range(len(tender_json['data']['features'])):
            number_of_feature_values = len(tender_json['data']['features'][feature]['enum'])
            values_json['parameters'].append({
                "code": tender_json['data']['features'][feature]['code'],
                "value": tender_json['data']['features'][feature]['enum'][randint(0, number_of_feature_values - 1)]['value']
            })
    return values_json


# generate json for bid
def generate_json_bid(user_idf, tender_json, lot_number=False):
    values = generate_bid_values(tender_json, lot_number)
    bid_json = {
                "data": {
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
                            },
                            "scale": "large"
                          }
                        ],
                        "subcontractingDetails": "ДКП «Книга», Україна, м. Львів, вул. Островського, 33"
                        }
                    }
    procurement_method = tender_json['data']['procurementMethodType']

    if procurement_method in limited_procurement:
        bid_json['data']['suppliers'] = bid_json['data']['tenderers']
        del bid_json['data']['tenderers']

    for key in values:
        bid_json['data'][key] = values[key]
    return bid_json


# create and activate bid for created tender
def make_bids(bids_quantity, tender_id, procurement_method, api_version, if_docs, tender_json):
    tender = TenderRequests(api_version)
    activate_bid_body = determine_procedure_for_bid(procurement_method)
    # bids_json = []
    if bids_quantity == 0:
        print('Bids haven\'t been made!')
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

            bid_json = generate_json_bid(identifier, tender_json)
            if procurement_method == 'belowThreshold':
                del bid_json["data"]["selfEligible"], bid_json["data"]["selfQualified"], bid_json["data"]["subcontractingDetails"]
            list_of_bids_json.append(bid_json)

            created_bid = tender.make_tender_bid(tender_id, bid_json, count)

            bid_token = created_bid.json()['access']['token']
            bid_id = created_bid.json()['data']['id']

            tender.activate_tender_bid(tender_id, bid_id, bid_token, activate_bid_body, count)

            bid_to_db(bid_id, bid_token, identifier, tender_id)  # save bid info to db

            if if_docs == 1:
                print("Documents will be added to bid!")
                document.add_documents_to_bid_ds(tender_id, bid_id, bid_token, procurement_method, api_version)
        return list_of_bids_json


def make_bid_competitive(list_of_bids, tender_id, api_version, procurement_method, if_docs):
    tender = TenderRequests(api_version)
    if len(list_of_bids) == 0:
        print('Bids haven\'t been made!')
    else:
        count = 0
        for bid in range(len(list_of_bids)):
            count += 1
            bid_json = list_of_bids[bid]
            created_bid = tender.make_tender_bid(tender_id, bid_json, count)
            if procurement_method == 'competitiveDialogueUA':
                activate_bid_body = {"data": {"status": "active"}}
            else:
                activate_bid_body = {"data": {"status": "pending"}}
            bid_token = created_bid.json()['access']['token']
            bid_id = created_bid.json()['data']['id']
            identifier = list_of_bids[bid]['data']['tenderers'][0]['identifier']['id']

            tender.activate_tender_bid(tender_id, bid_id, bid_token, activate_bid_body, count)

            if if_docs == 1:
                print("Documents will be added to bid!")
                document.add_documents_to_bid_ds(tender_id, bid_id, bid_token, '{}.stage2'.format(procurement_method), api_version)  # add .stage2 to procurementMethodType
            bid_to_db(bid_id, bid_token, identifier, tender_id)


def suppliers_for_limited(number_of_lots, tender_id, tender_token, list_of_id_lots, api_version, tender_json):
    tender = TenderRequests(api_version)
    supplier = 0
    if number_of_lots == 0:
        supplier += 1
        limited_supplier_json = generate_json_bid('00037256', tender_json)
        del limited_supplier_json["data"]["selfEligible"], limited_supplier_json["data"]["selfQualified"], limited_supplier_json["data"]["subcontractingDetails"]
        tender.add_supplier_limited(tender_id, tender_token, limited_supplier_json, supplier)
    else:
        for lot_id in range(len(list_of_id_lots)):
            supplier += 1
            limited_supplier_json = generate_json_bid('00037256', tender_json, supplier - 1)
            del limited_supplier_json["data"]["selfEligible"], limited_supplier_json["data"]["selfQualified"], limited_supplier_json["data"]["subcontractingDetails"]
            tender.add_supplier_limited(tender_id, tender_token, limited_supplier_json, supplier)
