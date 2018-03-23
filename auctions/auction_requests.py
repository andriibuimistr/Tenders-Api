# -*- coding: utf-8 -*-
from auction_data_for_requests import headers_request, host_selector, json_status_active_tendering, json_status_active
from flask import abort
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time
from datetime import datetime
import os
from pprint import pformat


def save_log(code, body, host, endpoint, method, request_name):
    now = datetime.now()
    path = os.path.join(os.getcwd(), 'logs', 'auctions', str(now.year), str(now.month), str(now.day), str(now.hour), '{} {} {}.txt'.format(code, datetime.now().strftime("%d-%m-%Y %H-%M-%S"), request_name))
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    f = open(path, "w+")
    try:
        body = json.loads(body)
    except Exception as e:
        print e
        body = body
    f.write('{} {}{}\n\n{}'.format(method, host, endpoint, pformat(body)))
    f.close()


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
                save_log(resp.status_code, resp.content, host, endpoint, method, request_name)
                return resp
        except HTTPError as error:
            print("{}: Error".format(request_name))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            save_log(error.response.status_code, resp.content, host, endpoint, method, request_name)
            time.sleep(1)
            if attempts >= 5:
                abort(error.response.status_code, resp.content)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                save_log(503, str(e), host, endpoint, method, request_name)
                abort(503, '{} error: {}'.format(request_name, e))
        except requests.exceptions.MissingSchema as e:
            print 'MissingSchema Exception'
            save_log(500, str(e), host, endpoint, method, request_name)
            abort(500, '{} error: {}'.format(request_name, e))
        except Exception as e:
            save_log(500, str(e), host, endpoint, method, request_name)
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
