# -*- coding: utf-8 -*-
from tender_data_for_requests import headers_request, host_selector, json_status_active_tendering, json_status_active
from flask import abort
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time


# Send request to cdb
def tenders_request_to_cdb(headers, host, endpoint, method, json_auction, request_name):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("HEAD", "{}".format(host))
            r = requests.Request(method, "{}{}".format(host, endpoint),
                                 data=json.dumps(json_auction),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            resp.raise_for_status()
            if resp.status_code in [200, 201, 202]:
                print("{}: Success".format(request_name))
                print("       status code:  {}".format(resp.status_code))
                return resp
        except HTTPError as error:
            print("{}: Error".format(request_name))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            time.sleep(1)
            if attempts >= 5:
                abort(error.response.status_code, error.message)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, '{} error: {}'.format(request_name, e))
        except requests.exceptions.MissingSchema as e:
            abort(500, '{} error: {}'.format(request_name, e))


class TenderRequests:

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = host_selector(cdb)
