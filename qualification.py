# -*- coding: utf-8 -*-
from data_for_tender import activate_contract_json
from database import Tenders, BidsTender
import requests
import key
import time
from tenders.tender_requests import TenderRequests

auth_key = key.auth_key


# headers for prequalification requests
headers_prequalification = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

# json for approve qualification
prequalification_approve_bid_json = {
  "data": {
    "status": "active",
    "qualified": True,
    "eligible": True
  }
}

# json for decline qualification
prequalification_decline_bid_json = {
  "data": {
    "status": "unsuccessful",
  }
}

# json for submit prequalification protocol
finish_prequalification_json = {
  "data": {
    "status": "active.pre-qualification.stand-still"
  }
}


def activate_award_json_select(procurement_method):
    if procurement_method == 'reporting':
        activate_award_json_negotiation = {
            "data": {
                "status": "active"
            }
        }
    else:
        activate_award_json_negotiation = {
                                  "data": {
                                    "status": "active",
                                    "qualified": True
                                  }
                                }
    return activate_award_json_negotiation


# get tender token from local DB (SQLA)
def get_tender_token(tender_id_long):
    try:
        token = Tenders.query.filter_by(tender_id_long=tender_id_long).first().tender_token
        return 0, token
    except Exception, e:
        return 1, e


# get list of qualifications for tender (SQLA)
def list_of_qualifications(tender_id_long, host, api_version):
    print 'Get list of qualifications'
    tender_json = requests.get("{}/api/{}/tenders/{}".format(host, api_version, tender_id_long))
    response = tender_json.json()
    qualifications = response['data']['qualifications']
    return qualifications


# select my bids
def pass_pre_qualification(qualifications, tender_id_long, tender_token, api_version):
    list_of_my_bids = BidsTender.query.filter_by(tender_id=tender_id_long).all()
    my_bids = []
    bids_json = []
    tender = TenderRequests(api_version)
    for x in range(len(list_of_my_bids)):  # select bid_id of every bid
        my_bids.append(list_of_my_bids[x].bid_id)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        qualification_bid_id = qualifications[x]['bidID']
        if qualification_bid_id in my_bids:
            time.sleep(1)
            action = tender.approve_prequalification(tender_id_long, qualification_id, tender_token, prequalification_approve_bid_json)
        else:
            time.sleep(1)
            action = tender.approve_prequalification(tender_id_long, qualification_id, tender_token, prequalification_decline_bid_json)
        bids_json.append(action)
    return bids_json


def pass_second_pre_qualification(qualifications, tender_id, tender_token, api_version):
    bids_json = []
    tender = TenderRequests(api_version)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        time.sleep(1)
        action = tender.approve_prequalification(tender_id, qualification_id, tender_token, prequalification_approve_bid_json)
        bids_json.append(action)
    return bids_json


def run_activate_award(host_kit, tender_id_long, tender_token, list_of_awards, procurement_method):
    tender = TenderRequests(host_kit[1])
    award_number = 0
    activate_award_json = activate_award_json_select(procurement_method)
    for award in range(len(list_of_awards)):
        award_number += 1
        award_id = list_of_awards[award]['id']
        tender.activate_award_contract(tender_id_long, 'awards', award_id, tender_token, activate_award_json, award_number)


def run_activate_contract(host_kit, tender_id_long, tender_token, list_of_contracts, complaint_end_date):
    tender = TenderRequests(host_kit[1])
    contract_number = 0
    json_activate_contract = activate_contract_json(complaint_end_date)
    for contract in range(len(list_of_contracts)):
        contract_number += 1
        contract_id = list_of_contracts[contract]['id']
        tender.activate_award_contract(tender_id_long, 'contracts', contract_id, tender_token, json_activate_contract, contract_number)
