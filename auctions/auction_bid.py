# -*- coding: utf-8 -*-
from faker import Faker
from random import randint
from database import db, BidsAuction
from cdb_requests import AuctionRequests

fake = Faker('uk_UA')


def json_for_bid_auction(procurement_method_type, identifier):
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
    if procurement_method_type == 'dgfOtherAssets':
        del(json_bid['data']['eligible'])
    return json_bid


activate_bid_json = {"data": {
                             "status": "active"
                             }
                     }


# add bid info to DB (SQLA)
def bid_to_db(bid_id, bid_token, u_identifier, auction_id):
    bid_to_sql = BidsAuction(None, bid_id, bid_token, auction_id, None, None, None, None, u_identifier)
    db.session.add(bid_to_sql)
    db.session.commit()
    db.session.remove()
    print 'Add auction bid to local database'
    return "success"


def create_bids(cdb, auction_id_long, procurement_method_type, number_of_bids):
    if number_of_bids == 0:
        print 'Bids haven\'t been made!'
    else:
        count = 0
        for bid in range(number_of_bids):
            count += 1
            identifier = str(randint(10000000, 99999999))
            bid = AuctionRequests(cdb)

            print 'Publish bid {}'.format(count)
            make_bid = bid.make_bid_auction(auction_id_long, json_for_bid_auction(procurement_method_type, identifier))

            print 'Activate bid {}'.format(count)
            bid.activate_auction_bid(auction_id_long, make_bid.json()['data']['id'], make_bid.json()['access']['token'])

            bid_to_db(make_bid.json()['data']['id'], make_bid.json()['access']['token'], identifier, auction_id_long)
