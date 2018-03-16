# -*- coding: utf-8 -*-
from data_for_auction_cdb1 import generate_auction_json
from data_for_auction_cdb2 import generate_auction_json_cdb_2
import time
from flask import abort
from database import db, Auctions
import refresh
import auction_validators
from auction_bid import create_bids
from auction_requests import AuctionRequests


# Add auction info to database
def auction_to_db(auction_id_long, auction_id_short, auction_token, procurement_method, auction_status, creator_id, cdb_version):
    try:
        # Try to connect to DB
        auction_to_sql = Auctions(None, auction_id_long, auction_id_short, auction_token, procurement_method, None, auction_status, None, None, None, None, creator_id, cdb_version)
        db.session.add(auction_to_sql)
        db.session.commit()
        print "Auction was added to local database"
        return {"status": "success"}, 0
    except Exception as e:
        abort(500, str(e))


def create_auction(ac_request, session):
    data = auction_validators.validator_create_auction(ac_request)  # validator of request data
    cdb_version = int(data['cdb_version'])
    number_of_items = int(data['number_of_items'])
    accelerator = int(data['accelerator'])
    company_id = int(data['company_id'])
    platform_host = data['platform_host']
    received_auction_status = data['auctionStatus']
    number_of_bids = int(data['number_of_bids'])
    procurement_method_type = data['procurementMethodType']

    if cdb_version == 1:
        json_auction = generate_auction_json(procurement_method_type, number_of_items, accelerator, data['steps'])
    else:
        json_auction = generate_auction_json_cdb_2(number_of_items, accelerator, data['min_number_of_qualified_bids'], data['rent'])

    auction = AuctionRequests(cdb_version)
    a_publish = auction.publish_auction(json_auction)

    auction_id_long = a_publish.json()['data']['id']
    auction_token = a_publish.json()['access']['token']
    auction_id_short = a_publish.json()['data']['auctionID']

    time.sleep(1)
    a_activate = auction.activate_auction(auction_id_long, auction_token)
    auction_status = a_activate.json()['data']['status']

    auction_to_db(auction_id_long, auction_id_short, auction_token, procurement_method_type, auction_status, session['user_id'], cdb_version)  # add auction data to database
    create_bids(cdb_version, auction_id_long, procurement_method_type, number_of_bids)  # make bids
    add_auction_to_company = refresh.add_one_tender_company(company_id, platform_host, auction_id_long, 'auction')  # add auction to local database

    # Initial 'Response JSON' data
    response_json = dict()
    response_json['tender_to_company'] = add_auction_to_company[0], add_auction_to_company[2] + auction_id_short
    response_json['id'] = auction_id_short
    response_json['status'] = 'error'
    response_code = 0
    response_json['auctionStatus'] = 'undefined'

    if received_auction_status == 'active.tendering':
        if auction_status == 'active.tendering':
            response_json['auctionStatus'] = auction_status
            response_json['status'] = 'success'
            response_code = 201

    return response_json, response_code
