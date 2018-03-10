# -*- coding: utf-8 -*-
from data_for_requests import headers_request, host_selector
from data_for_auction_cdb1 import generate_auction_json
from requests.exceptions import ConnectionError
import requests
import time
import json
from flask import abort
from database import db, Auctions
import refresh
from refresh import get_auction_info
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


# save auction info to DB (SQLA)
def auction_to_db(auction_id_long, auction_id_short, auction_token, procurement_method, auction_status, creator_id, cdb_version):
    try:
        # Connect to DB
        auction_to_sql = Auctions(None, auction_id_long, auction_id_short, auction_token, procurement_method, None, auction_status, None, None, None, None, creator_id, cdb_version)
        db.session.add(auction_to_sql)
        db.session.commit()
        print "Auction was added to local database"
        return {"status": "success"}, 0
    except Exception as e:
        return e, 1


def create_auction(ac_request, session):
    cdb_version = int(ac_request['cdb_version'])
    procurement_method_type = ac_request['procurementMethodType']
    number_of_items = int(ac_request['number_of_items'])
    accelerator = int(ac_request['accelerator'])
    company_id = int(ac_request['company_id'])
    platform_host = ac_request['platform_host']
    received_auction_status = ac_request['auctionStatus']

    host_data = host_selector(1)
    json_auction = generate_auction_json(procurement_method_type, number_of_items, accelerator)
    # pprint(json_auction)
    headers_auction = headers_request(json_auction, host_data[1], cdb_version)
    publish_auction_response = publish_auction(headers_auction, json_auction, host_data[0])  # publish auction in draft status

    time.sleep(1)
    activate_auction_response = activate_auction(publish_auction_response[1], headers_auction, host_data[0])

    auction_status = activate_auction_response[1].json()['data']['status']
    auction_id_long = publish_auction_response[1].json()['data']['id']
    auction_id_short = publish_auction_response[1].json()['data']['auctionID']
    auction_token = publish_auction_response[1].json()['access']['token']

    add_auction_db = auction_to_db(auction_id_long, auction_id_short, auction_token, procurement_method_type, auction_status, session['user_id'], cdb_version)
    if add_auction_db[1] == 1:
        abort(500, '{}'.format(add_auction_db[0]))

    add_tender_company = refresh.add_one_tender_company(company_id, platform_host, auction_id_long, 'auction')

    # Response JSON data
    response_json = dict()
    response_json['tender_to_company'] = add_tender_company[0], add_tender_company[2] + auction_id_short
    response_json['id'] = auction_id_short
    response_json['status'] = 'error'
    response_code = 0
    response_json['auctionStatus'] = 'undefined'

    if received_auction_status == 'active.tendering':
        get_t_info = get_auction_info(host_data, auction_id_long)

        if get_t_info[1].json()['data']['status'] == 'active.tendering':
            response_json['auctionStatus'] = get_t_info[1].json()['data']['status']
            response_json['status'] = 'success'
            response_code = 201
        else:
            response_json['auctionStatus'] = get_t_info[1].json()['data']['status']
            response_code = 422

    return response_json, response_code


