import tender_additional_data
from key import auth_key
import json


# Select host for CDB
def host_selector(cdb_version):
    if cdb_version == 'dev':
        host = 'https://api-sandbox.prozorro.openprocurement.net/api/dev/tenders'
        host_public = 'https://public.api-sandbox.prozorro.openprocurement.net/api/dev/tenders'
    else:
        host = 'https://lb.api-sandbox.openprocurement.org/api/2.4/tenders'
        host_public = 'https://public.api-sandbox.openprocurement.org/api/2.4/tenders'
    return host, host_public


# generate headers for create tender
def headers_request(cdb_version, json_data):
    if cdb_version == 'dev':
        host_headers = 'api-sandbox.prozorro.openprocurement.net'
    else:
        host_headers = 'lb.api-sandbox.openprocurement.org'
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_data))),
               "Content-Type": "application/json",
               "Host": host_headers}
    return headers


json_status_active = {
    "data": {
        "status": "active"
    }
}

json_finish_first_stage = {
    "data": {
        "status": "active.stage2.waiting"
    }
}

json_finish_pq = {
    "data": {
        "status": "active.pre-qualification.stand-still"
    }
}


def json_activate_tender(procurement_method):
    if procurement_method in tender_additional_data.above_threshold_procurement:
        activate_tender_json = {
            "data": {
                "status": "active.tendering"
            }
        }
    elif procurement_method in tender_additional_data.below_threshold_procurement:
        activate_tender_json = {
            "data": {
                "status": "active.enquiries"
            }
        }
    else:
        activate_tender_json = {
            "data": {
                "status": "active"
            }
        }
    return activate_tender_json


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