# -*- coding: utf-8 -*-
from variables import Tenders, Bids, activate_contract_json
import requests
import key
import json
import time
from flask import abort
from requests.exceptions import ConnectionError

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


# approve/cancel qualifications
def approve_prequalification(qualification_id, prequalification_bid_json, tender_id_long, tender_token, qualification_bid_id, is_my_bid, host, api_version):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("HEAD", "{}/api/{}/tenders".format(host, api_version))
            r = requests.Request('PATCH',
                                 "{}/api/{}/tenders/{}/qualifications/{}?acc_token={}".format(host, api_version, tender_id_long, qualification_id, tender_token),
                                 data=json.dumps(prequalification_bid_json),
                                 headers=headers_prequalification,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            print("Approve bid:")
            if resp.status_code == 200:
                print("       status code:  {}".format(resp.status_code))
                approve_json = {"isMyBid": is_my_bid, "bidID": qualification_bid_id, "qualificationID": qualification_id, "status_code": resp.status_code}
                return approve_json
            else:
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                approve_json = {"isMyBid": is_my_bid, "bidID": qualification_bid_id, "qualificationID": qualification_id, "status_code": resp.status_code,
                                "description": json.loads(resp.content)['errors'][0]['description']}
                if attempts >= 5:
                    return approve_json
        except Exception as e:
            if attempts < 5:
                continue
            else:
                print e
                return {"bidID": qualification_bid_id, "status_code": 500, "reason": str(e)}


# select my bids
def pass_pre_qualification(qualifications, tender_id_long, tender_token, host, api_version):
    list_of_my_bids = Bids.query.filter_by(tender_id=tender_id_long).all()
    my_bids = []
    bids_json = []
    for x in range(len(list_of_my_bids)):  # select bid_id of every bid
        my_bids.append(list_of_my_bids[x].bid_id)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        qualification_bid_id = qualifications[x]['bidID']
        if qualification_bid_id in my_bids:
            time.sleep(1)
            action = approve_prequalification(qualification_id, prequalification_approve_bid_json, tender_id_long, tender_token, qualification_bid_id, True, host, api_version)
        else:
            time.sleep(1)
            action = approve_prequalification(qualification_id, prequalification_decline_bid_json, tender_id_long, tender_token, qualification_bid_id, False, host, api_version)
        bids_json.append(action)
    return bids_json


def pass_second_pre_qualification(qualifications, tender_id, tender_token, host, api_version):
    bids_json = []
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        qualification_bid_id = qualifications[x]['bidID']
        time.sleep(1)
        action = approve_prequalification(qualification_id, prequalification_approve_bid_json, tender_id, tender_token, qualification_bid_id, True, host, api_version)
        bids_json.append(action)
    return bids_json


# submit protocol of prequalification
def finish_prequalification(tender_id_long, tender_token, host, api_version):
    try:
        s = requests.Session()
        s.request("HEAD", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}?acc_token={}".format(host, api_version, tender_id_long, tender_token),
                             data=json.dumps(finish_prequalification_json),
                             headers=headers_prequalification,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Finish prequalification:")
        if resp.status_code == 200:
            print("       status code:  {}".format(resp.status_code))
            f_prequalification_json = {"status code": resp.status_code}
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            f_prequalification_json = {"status_code": resp.status_code, "reason": resp.content}
        return f_prequalification_json
    except Exception as e:
        print e
        return {"status_code": 500, "reason": str(e)}


def activate_award_contract(headers_tender, host_kit, tender_id_long, tender_token, award_approve_json, id_for_activate, type_of, number):
    if type_of == 'award':
        type_to_activate = 'awards'
    else:
        type_to_activate = 'contracts'

    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("GET", "{}/api/{}/tenders".format(host_kit[0], host_kit[1]))
            r = requests.Request('PATCH', "{}/api/{}/tenders/{}/{}/{}?acc_token={}".format(host_kit[0], host_kit[1], tender_id_long, type_to_activate, id_for_activate, tender_token),
                                 data=json.dumps(award_approve_json),
                                 headers=headers_tender,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print("Activating {} {}: Success".format(type_of, number))
                print("       status code:  {}".format(resp.status_code))
                # activate_tender_response = {"status_code": resp.status_code}
                return resp.status_code, resp.content
            else:
                print("Activating {} {}: Error".format(type_of, number))
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                time.sleep(1)
                if attempts >= 5:
                    abort(resp.status_code, 'Activate {} error: '.format(type_of) + resp.content)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Activate {} error: {}'.format(type_of, e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Activate {} error: {}'.format(type_of, e))


def run_activate_award(headers_tender, host_kit, tender_id_long, tender_token, list_of_awards, procurement_method):
    award_number = 0
    activate_award_json = activate_award_json_select(procurement_method)
    for award in range(len(list_of_awards)):
        award_number += 1
        award_id = list_of_awards[award]['id']
        activate_award_contract(headers_tender, host_kit, tender_id_long, tender_token, activate_award_json, award_id, 'award', award_number)


def run_activate_contract(headers_tender, host_kit, tender_id_long, tender_token, list_of_contracts, complaint_end_date):
    contract_number = 0
    json_activate_contract = activate_contract_json(complaint_end_date)
    for contract in range(len(list_of_contracts)):
        contract_number += 1
        contract_id = list_of_contracts[contract]['id']
        activate_award_contract(headers_tender, host_kit, tender_id_long, tender_token, json_activate_contract, contract_id, 'contract', contract_number)

