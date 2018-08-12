import json
from key import auth_key, auth_key_ds, key_monitoring, key_cdb1, key_cdb2
from tenders.tender_additional_data import above_threshold_procurement, below_threshold_procurement


# function for decode (convert) bytes-like objects in dictionary to string
def json_bytes_to_string(json_bytes):
    for key in json_bytes:
        if type(json_bytes[key]) == bytes:
            json_bytes[key] = json_bytes[key].decode("utf-8")
        elif type(json_bytes[key]) == dict:
            json_bytes_to_string(json_bytes[key])
        elif type(json_bytes[key]) == list:
            for element in json_bytes[key]:
                json_bytes_to_string(element)
    return json_bytes


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


def tender_headers_request(json_data):
    headers = {"Authorization": "Basic {}".format(auth_key.decode("utf-8")),
               "Content-Length": "{}".format(len(json.dumps(json_bytes_to_string(json_data)))),
               "Content-Type": "application/json"}
    return headers


tender_headers_add_document_ds = {'authorization': "Basic {}".format(auth_key_ds)}
tender_headers_patch_document_ds = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "application/json",
    'cache-control': "no-cache",
    }
monitoring_headers = {"Authorization": "Basic {}".format(key_monitoring.decode("utf-8")),
                      "Content-Type": "application/json"}  # "Host": "audit-api-sandbox.prozorro.gov.ua"


def auction_host_selector(cdb_number):
    if cdb_number == 1:
        host = 'https://lb.api-sandbox.ea.openprocurement.org/api/2.5/auctions'
    else:
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/auctions'
    return host


def auction_headers_request(cdb_number, json_data, token=None):
    if cdb_number == 1:
        key = key_cdb1
        host_headers = 'lb.api-sandbox.ea.openprocurement.org'
    else:
        key = key_cdb2
        host_headers = 'lb.api-sandbox.ea2.openprocurement.net'
    headers = {"Authorization": "Basic {}".format(key.decode("utf-8")),
               "Content-Length": "{}".format(len(json.dumps(json_bytes_to_string(json_data)))),
               "Content-Type": "application/json",
               "X-Access-Token": token,
               "Host": host_headers}
    return headers


def privatization_host_selector(entity):
    if entity == 'asset':
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/assets'
    elif entity == 'transfer':
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/transfers'
    else:
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/lots'
    return host


def json_status(status):
    status_json = {"data": {"status": status}}
    return status_json


def json_activate_tender(procurement_method):
    if procurement_method in above_threshold_procurement:
        activate_tender_json = json_status('active.tendering')
    elif procurement_method in below_threshold_procurement:
        activate_tender_json = json_status('active.enquiries')
    else:
        activate_tender_json = json_status('active')
    return activate_tender_json


prequalification_approve_bid_json = {
    "data": {
        "status": "active",
        "qualified": True,
        "eligible": True
    }
}


def activate_award_limited_json(procurement_method):
    json_activate_award_limited = json_status('active')
    if procurement_method != 'reporting':
        json_activate_award_limited['data']['qualified'] = True
    return json_activate_award_limited


transfer_json = {"data": {}}


def json_activate_auction_p(token):
    json_activate = json_status('active.tendering')
    json_activate['access'] = {"token": token}
    return json_activate
