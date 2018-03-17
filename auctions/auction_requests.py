# -*- coding: utf-8 -*-
from auction_data_for_requests import headers_request, host_selector, json_status_active_tendering, json_status_active
from flask import abort
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time


# Send request to cdb
def request_to_cdb(headers, host, endpoint, method, json_request, request_name):
    attempts = 0
    for x in range(5):
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
                abort(error.response.status_code, resp.content)
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


class AuctionRequests:

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = host_selector(cdb)

    def publish_auction(self, json_auction):
        return request_to_cdb(headers_request(self.cdb, json_auction), self.host, '', 'POST', json_auction, 'Publish auction')

    def activate_auction(self, auction_id_long, token):
        return request_to_cdb(headers_request(self.cdb, json_status_active_tendering), self.host, '/{}?acc_token={}'.format(auction_id_long, token), 'PATCH', json_status_active_tendering, 'Activate auction')

    def make_bid_auction(self, auction_id_long, json_bid):
        return request_to_cdb(headers_request(self.cdb, json_bid), self.host, '/{}/bids'.format(auction_id_long), 'POST', json_bid, 'Publish auction bid')

    def activate_auction_bid(self, auction_id_long, bid_id, bid_token):
        return request_to_cdb(headers_request(self.cdb, json_status_active), self.host, '/{}/bids/{}?acc_token={}'.format(auction_id_long, bid_id, bid_token), 'PATCH', json_status_active, 'Activate auction bid')

    def get_auction_info(self, auction_id_long):
        return request_to_cdb(None, self.host, '/{}'.format(auction_id_long), 'GET', None, 'Get auction info')
