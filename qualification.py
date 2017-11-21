# -*- coding: utf-8 -*-
from variables import Tenders, Bids
import requests
import key
import json
import time


auth_key = key.auth_key
api_version = "2.3"

host = "https://lb.api-sandbox.openprocurement.org"


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


# get tender token from local DB (SQLA)
def get_tender_token(tender_id_long):
    try:
        token = Tenders.query.filter_by(tender_id_long=tender_id_long).first().tender_token
        return token
    except:
        raise Exception()


# get list of qualifications for tender (SQLA)
def list_of_qualifications(tender_id_long):
    tender_json = requests.get("{}/api/{}/tenders/{}".format(host, api_version, tender_id_long))
    response = tender_json.json()
    qualifications = response['data']['qualifications']
    return qualifications


# approve/cancel qualifications
def approve_prequalification(qualification_id, prequalification_bid_json, tender_id_long, tender_token,
                             qualification_bid_id, is_my_bid):
    try:
        s = requests.Session()
        s.request("HEAD", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}/qualifications/{}?acc_token={}".format(
                                 host, api_version, tender_id_long, qualification_id, tender_token),
                             data=json.dumps(prequalification_bid_json),
                             headers=headers_prequalification,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Approve bid:")
        if resp.status_code == 200:
            print("       status code:  {}".format(resp.status_code))
            approve_json = {"isMyBid": is_my_bid, "bidID": qualification_bid_id, "qualificationID": qualification_id,
                            "status code": resp.status_code}
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            approve_json = {"isMyBid": is_my_bid, "bidID": qualification_bid_id, "qualificationID": qualification_id,
                            "status code": resp.status_code,
                            "description": json.loads(resp.content)['errors'][0]['description']}
        return approve_json
    except Exception as e:
        print e
        return {"bidID": qualification_bid_id, "status code": 500, "reason": str(e)}


# select my bids
def select_my_bids(qualifications, tender_id_long, tender_token):
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
            action = approve_prequalification(qualification_id, prequalification_approve_bid_json, tender_id_long,
                                              tender_token, qualification_bid_id, True)
        else:
            time.sleep(1)
            action = approve_prequalification(qualification_id, prequalification_decline_bid_json, tender_id_long,
                                              tender_token, qualification_bid_id, False)
        bids_json.append(action)
    return bids_json


# submit protocol of prequalification
def finish_prequalification(tender_id_long, tender_token):
    try:
        s = requests.Session()
        s.request("HEAD", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}?acc_token={}".format(
                                 host, api_version, tender_id_long, tender_token),
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
            f_prequalification_json = {"status code": resp.status_code, "reason": resp.content}
        return f_prequalification_json
    except Exception as e:
        print e
        return {"status code": 500, "reason": str(e)}
