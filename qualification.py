# -*- coding: utf-8 -*-
from variables import Tenders, Bids, activate_contract_json
import requests
import key
import json
import time


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
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            approve_json = {"isMyBid": is_my_bid, "bidID": qualification_bid_id, "qualificationID": qualification_id, "status_code": resp.status_code,
                            "description": json.loads(resp.content)['errors'][0]['description']}
        return approve_json
    except Exception as e:
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


def activate_award(headers_tender, host_kit, tender_id_long, tender_token, award_approve_json, award_id):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("GET", "{}/api/{}/tenders".format(host_kit[0], host_kit[1]))
            r = requests.Request('PATCH', "{}/api/{}/tenders/{}/awards/{}?acc_token={}".format(host_kit[0], host_kit[1], tender_id_long, award_id, tender_token),
                                 data=json.dumps(award_approve_json),
                                 headers=headers_tender,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print("Activating award: Success")
                print("       status code:  {}".format(resp.status_code))
                # activate_tender_response = {"status_code": resp.status_code}
                return 0, resp, resp.content, resp.status_code
            else:
                print("Activating award: Error")
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                if attempts >= 5:
                    return 0, resp, resp.content, resp.status_code
        except Exception as e:
            if attempts < 5:
                continue
            else:
                return 1, 'Activate award error: ' + str(e)


def activate_contract(headers_tender, host_kit, tender_id_long, tender_token, json_activate_contract, contract_id):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("GET", "{}/api/{}/tenders".format(host_kit[0], host_kit[1]))
            r = requests.Request('PATCH', "{}/api/{}/tenders/{}/contracts/{}?acc_token={}".format(host_kit[0], host_kit[1], tender_id_long, contract_id, tender_token),
                                 data=json.dumps(json_activate_contract),
                                 headers=headers_tender,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print("Activating contract: Success")
                print("       status code:  {}".format(resp.status_code))
                # activate_tender_response = {"status_code": resp.status_code}
                return resp.status_code, resp.content
            else:
                print("Activating contract: Error. Attempt {}".format(attempts))
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                if attempts >= 5:
                    return resp.status_code, resp.content
        except Exception as e:
            if attempts < 5:
                continue
            else:
                return 500, 'Activate contract error: ' + str(e)


def run_activate_award(headers_tender, host_kit, tender_id_long, tender_token, list_of_awards, procurement_method):
    activate_award_json = activate_award_json_select(procurement_method)
    for award in range(len(list_of_awards)):
        award_id = list_of_awards[award]['id']
        send_activate_award = activate_award(headers_tender, host_kit, tender_id_long, tender_token, activate_award_json, award_id)


def run_activate_contract(headers_tender, host_kit, tender_id_long, tender_token, list_of_contracts, complaint_end_date):
    json_activate_contract = activate_contract_json(complaint_end_date)
    for contract in range(len(list_of_contracts)):
        contract_id = list_of_contracts[contract]['id']
        send_activate_contract = activate_contract(headers_tender, host_kit, tender_id_long, tender_token, json_activate_contract, contract_id)
        if send_activate_contract[0] == 500:
            return send_activate_contract[0], send_activate_contract[1]
        elif send_activate_contract[0] not in [500, 200]:
            return send_activate_contract[0], send_activate_contract[1]
    return 200, 'Success'
