from key import auth_key
import json


# Select host for CDB
def host_selector(cdb_version):
    if cdb_version == 'dev':
        host = 'https://api-sandbox.prozorro.openprocurement.net/api/dev/tenders'
    else:
        host = 'https://lb.api-sandbox.openprocurement.org/api/2.4/tenders'
    return host


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


json_status_active_tendering = {
                            "data": {
                                "status": "active.tendering"
                            }
                        }

json_status_active = {"data": {
                             "status": "active"
                             }
                      }
