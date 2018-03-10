from key import key_cdb1, key_cdb2
import json


# Select host for CDB
def host_selector(cdb_number):
    if cdb_number == 1:
        host = 'https://lb.api-sandbox.ea.openprocurement.org/api/2.5/auctions'
        host_headers = 'lb.api-sandbox.ea.openprocurement.org'
    else:
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/auctions'
        host_headers = 'lb.api-sandbox.ea2.openprocurement.net'
    return host, host_headers


# generate headers for create auction
def headers_request(json_auction, headers_host, cdb_number):
    if cdb_number == 1:
        auth_key = key_cdb1
    else:
        auth_key = key_cdb2
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_auction))),
               "Content-Type": "application/json",
               "Host": headers_host}
    return headers