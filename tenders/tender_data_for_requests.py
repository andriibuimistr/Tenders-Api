from tender_additional_data import *
from key import auth_key, auth_key_ds, key_monitoring
import json


# Select host for CDB
def tender_host_selector(cdb_version):
    if cdb_version == 'dev':
        host = 'https://api-sandbox.prozorro.openprocurement.net/api/dev/tenders'
        host_public = 'https://public.api-sandbox.prozorro.openprocurement.net/api/dev/tenders'
    else:
        host = 'https://lb.api-sandbox.openprocurement.org/api/2.4/tenders'
        host_public = 'https://public.api-sandbox.openprocurement.org/api/2.4/tenders'
    return host, host_public


def tender_ds_host_selector(cdb_version):
    if cdb_version == 'dev':
        host = 'https://upload.docs-sandbox.prozorro.openprocurement.net/upload'
    else:
        host = 'https://upload.docs-sandbox.openprocurement.org/upload'
    return host


monitoring_host = 'https://audit-api-sandbox.prozorro.gov.ua/api/2.4/monitorings'


# generate headers for create tender
def tender_headers_request(cdb_version, json_data, monitoring=False):
    # if cdb_version == 'dev':
    #     host_headers = 'api-sandbox.prozorro.openprocurement.net'
    # else:
    #     host_headers = 'lb.api-sandbox.openprocurement.org'
    #     if monitoring:
    #         host_headers = 'audit-api-sandbox.prozorro.gov.ua'
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_data))),
               "Content-Type": "application/json"}  # "Host": host_headers
    return headers


tender_headers_add_document_ds = {
    'authorization': "Basic {}".format(auth_key_ds)
    }

tender_headers_patch_document_ds = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

monitoring_headers = {"Authorization": "Basic {}".format(key_monitoring),
                      "Content-Type": "application/json"}  # "Host": "audit-api-sandbox.prozorro.gov.ua"


json_status_active = {
    "data": {
        "status": "active"
    }
}

json_status_completed = {
    "data": {
        "status": "completed"
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
    if procurement_method in above_threshold_procurement:
        activate_tender_json = {
            "data": {
                "status": "active.tendering"
            }
        }
    elif procurement_method in below_threshold_procurement:
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


json_status_addressed = {"data": {
                                "status": "addressed"
                              }
                         }

json_status_declined = {"data": {
                                "status": "declined"
                              }
                         }
