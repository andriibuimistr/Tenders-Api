# -*- coding: utf-8 -*-
from data_for_requests import headers_request, host_selector
from data_for_auction_cdb1 import generate_auction_json
from requests.exceptions import ConnectionError
import requests
import time
import json
from flask import abort
from pprint import pprint


# Publish auction
def publish_auction(headers, json_auction, host):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("GET", "{}".format(host))
            r = requests.Request('POST', "{}".format(host),
                                 data=json.dumps(json_auction),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))

            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 201:
                print("Publishing auction: Success")
                print("       status code:  {}".format(resp.status_code))
                return 0, resp, resp.content, resp.status_code
            else:
                print("Publishing auction: Error")
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                time.sleep(1)
                if attempts >= 5:
                    abort(resp.status_code, resp.content)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Publish auction error: ' + str(e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Publish auction error: ' + str(e))


# Activate auction
def activate_auction(publish_auction_response, headers, host):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            activate_auction_json = json.loads('{ "data": { "status": "active.tendering"}}')
            auction_location = publish_auction_response.headers['Location']
            token = publish_auction_response.json()['access']['token']
            s = requests.Session()
            s.request("GET", "{}".format(host))
            r = requests.Request('PATCH', "{}{}{}".format(auction_location, '?acc_token=', token),
                                 data=json.dumps(activate_auction_json),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print("Activating auction: Success")
                print("       status code:  {}".format(resp.status_code))
                return 0, resp, resp.content, resp.status_code
            else:
                print("Activating auction: Error")
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                time.sleep(1)
                if attempts >= 5:
                    abort(resp.status_code, resp.content)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Activate auction error: ' + str(e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Activate auction error: ' + str(e))


def create_auction(cdb_version, procurement_method_type, number_of_items, accelerator):
    host_data = host_selector(1)
    json_auction = generate_auction_json(procurement_method_type, number_of_items, accelerator)
    # pprint(json_auction)
    headers_auction = headers_request(json_auction, host_data[1], cdb_version)
    publish_auction_response = publish_auction(headers_auction, json_auction, host_data[0])  # publish auction in draft status

    time.sleep(1)
    activate_auction_response = activate_auction(publish_auction_response[1], headers_auction, host_data[0])
    print activate_auction_response[1].json()


create_auction(1, 'dgfFinancialAssets', 2, 720)
