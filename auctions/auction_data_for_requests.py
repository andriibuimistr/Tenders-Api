from key import key_cdb1, key_cdb2
import json


# Select host for CDB
def auction_host_selector(cdb_number):
    if cdb_number == 1:
        host = 'https://lb.api-sandbox.ea.openprocurement.org/api/2.5/auctions'
    else:
        host = 'https://lb.api-sandbox.ea2.openprocurement.net/api/2.3/auctions'
    return host


# generate headers for create auction
def auction_headers_request(cdb_number, json_data):
    if cdb_number == 1:
        authorization = "Basic {}".format(key_cdb1)
        host_headers = 'lb.api-sandbox.ea.openprocurement.org'
    else:
        authorization = "Bearer {}".format(key_cdb2)
        host_headers = 'lb.api-sandbox.ea2.openprocurement.net'
    headers = {"Authorization": authorization,
               "Content-Length": "{}".format(len(json.dumps(json_data))),
               "Content-Type": "application/json",
               "Host": host_headers}
    return headers


json_status_active_tendering = {
                            "data": {
                                "status": "active.tendering"
                            }
                        }

json_status_active = {"data": {
                             "status": "active"
                             }
                      }
