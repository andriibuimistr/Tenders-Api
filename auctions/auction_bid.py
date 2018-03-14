# -*- coding: utf-8 -*-
from requests.exceptions import ConnectionError
from faker import Faker
import requests
from random import randint
import json
import time
from flask import abort
from database import db, BidsAuction

fake = Faker('uk_UA')


def json_for_bid_auction(procurementMethodType, identifier):
    json_bid = {"data": {
                    "status": "draft",
                    "qualified": True,
                    "eligible": True,
                    "value": {
                      "amount": randint(11000, 15000)
                    },
                    "tenderers": [
                      {
                        "contactPoint": {
                          "telephone": "+380 (432) 21-69-30",
                          "name": "Сергій Олексюк",
                          "email": "soleksuk@gmail.com"
                        },
                        "identifier": {
                          "scheme": "UA-EDR",
                          "id": identifier,
                          "uri": "http://site.site"
                        },
                        "name": fake.company(),
                        "additionalIdentifiers": [
                              {
                                "scheme": "UA-FIN",
                                "id": "А01 457213"
                              }
                            ],
                        "address": {
                          "countryName": "Україна",
                          "postalCode": "21100",
                          "region": "м. Вінниця",
                          "streetAddress": "вул. Островського, 33",
                          "locality": "м. Вінниця"
                        }
                      }
                    ]
                  }
                }
    if procurementMethodType == 'dgfOtherAssets':
        del(json_bid['data']['eligible'])
    return json_bid


activate_bid_json = {"data": {
                             "status": "active"
                             }
                     }


# create bid
def make_bid_auction(headers, host, auction_id, bid_json, bid_number):
    attempts = 0
    for x in range(5):
        attempts += 1
        print '{}{}'.format('Publishing bid: Attempt ', attempts)
        try:
            s = requests.Session()
            s.request('HEAD', '{}'.format(host))
            r = requests.Request('POST', '{}/{}/bids'.format(host, auction_id),
                                 data=json.dumps(bid_json),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 201:
                print('{}{}: {}'.format('Publishing bid ', bid_number, 'Success'))
                print("       status code:  {}".format(resp.status_code))
                return 0, resp, resp.content, resp.status_code
            else:
                print('{}{}: {}'.format('Publishing bid ', bid_number, 'Error'))
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
            # bid_location = resp.headers['Location']  # get url of created bid
            # bid_token = resp.json()['access']['token']  # get token of created bid
            # bid_id = resp.json()['data']['id']  # get id of created bid
            time.sleep(1)
            if attempts >= 5:
                abort(resp.status_code, resp.content)
        except ConnectionError as e:
            print 'Connection Error'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Publish bid error: ' + str(e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Publish bid error: ' + str(e))


# activate created bid
def activate_bid(headers, host, mb_response, json_bid_active, bid_number):
    attempts = 0
    for x in range(5):
        attempts += 1
        print '{}{}'.format('Activating bid: Attempt ', attempts)
        try:
            s = requests.Session()
            s.request("HEAD", "{}".format(host))
            r = requests.Request('PATCH',
                                 "{}{}{}".format(mb_response.headers['Location'], '?acc_token=', mb_response.json()['access']['token']),
                                 data=json.dumps(json_bid_active),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print('{}{}: {}'.format('Activating bid ', bid_number,  'Success'))
                print("       status code:  {}".format(resp.status_code))
                return 0, resp, resp.content, resp.status_code
            else:
                print('{}{}: {}'.format('Activating bid ', bid_number,  'Error'))
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
                abort(500, 'Activate bid error: ' + str(e))
        except requests.exceptions.MissingSchema as e:
            abort(500, 'Activate bid error: ' + str(e))


# add bid info to DB (SQLA)
def bid_to_db(bid_id, bid_token, u_identifier, auction_id):
    bid_to_sql = BidsAuction(None, bid_id, bid_token, auction_id, None, None, None, None, u_identifier)
    db.session.add(bid_to_sql)
    db.session.commit()  # you need to call commit() method to save your changes to the database
    print 'Add auction bid to local database'
    return "success"


def create_bids(headers, host, auction_id, procurementMethodType, number_of_bids):
    if number_of_bids == 0:
        print 'Bids haven\'t been made!'
    else:
        count = 0
        for bid in range(number_of_bids):
            count += 1
            identifier = "00137256"
            make_bid = make_bid_auction(headers, host, auction_id, json_for_bid_auction(procurementMethodType, identifier), count)
            activate_bid(headers, host, make_bid[1], activate_bid_json, count)
            add_bid_db = bid_to_db(make_bid[1].json()['data']['id'], make_bid[1].json()['access']['token'], identifier, auction_id)


