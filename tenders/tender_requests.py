# -*- coding: utf-8 -*-
from tender_data_for_requests import headers_request, host_selector, json_status_active_tendering, json_status_active
from flask import abort
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time


# Send request to cdb
def request_to_cdb(headers, host, endpoint, method, json_request, request_name):
    attempts = 0
    for x in range(5):
        print '!!!Request'
        attempts += 1
        try:
            s = requests.Session()
            s.request("HEAD", "{}".format(host))
            r = requests.Request(method, "{}{}".format(host, endpoint),
                                 data=json.dumps(json_request),
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
        except Exception as e:
            abort(500, '{} error: {}'.format(request_name, e))


class TenderRequests:

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = host_selector(cdb)

    def publish_tender(self, json_tender):
        return request_to_cdb(headers_request(self.cdb, json_tender), self.host, '', 'POST', json_tender, 'Publish tender')

    def activate_tender(self, tender_id_long, token):
        return request_to_cdb(headers_request(self.cdb, json_status_active_tendering), self.host, '/{}?acc_token={}'.format(tender_id_long, token), 'PATCH', json_status_active_tendering, 'Activate tender')

    def get_tender_info(self, tender_id_long):
        return request_to_cdb(None, self.host, '/{}'.format(tender_id_long), 'GET', None, 'Get tender info')
