# -*- coding: utf-8 -*-
from auction_additional_data import *
from flask import abort
import core
from database import BidsAuction, Auctions, db
from language.translations import alert


def validator_create_auction(data):
    for field in range(len(create_auction_required_fields)):
        if create_auction_required_fields[field] not in data:
            abort(400, "Field '{}' is required. List of required fields: {}".format(create_auction_required_fields[field], create_auction_required_fields))

    valid_data = dict()

    if 'procurementMethodType' not in data:
        abort(400, 'procurementMethodType is required')
    if data['procurementMethodType'] not in auction_procurement_method_types:
        abort(400, 'procurementMethodType must be one of {}'.format(auction_procurement_method_types))

    if str(data['number_of_items']).isdigit() is False:
        abort(400, 'Number of items must be integer')
    if 1 > int(data['number_of_items']) or int(data['number_of_items']) > 20:
        abort(422, 'Number of items must be between 1 and 20')

    if len(data["number_of_bids"]) != 0:
        if str(data["number_of_bids"]).isdigit() is False:
            abort(400, 'Number of bids must be integer')
        if 0 > int(data["number_of_bids"]) or int(data["number_of_bids"]) > 10:
            abort(422, 'Number of bids must be between 0 and 10')
        valid_data["number_of_bids"] = data["number_of_bids"]
    else:
        valid_data["number_of_bids"] = '0'

    if str(data['accelerator']).isdigit() is False:
        abort(400, 'Accelerator must be integer')
    if 1 > int(data['accelerator']) or int(data['accelerator']) > 1440:
        abort(422, 'Accelerator must be between 1 and 1440')

    if str(data['company_id']).isdigit() is False:
        abort(400, 'Company ID must be integer')
    if int(data['company_id']) == 0:
        abort(422, 'Company id can\'t be 0')

    if data['auctionStatus'] not in auction_status_to_create:
        abort(422, 'Tender status must be one of: {}'.format(auction_status_to_create))

    if data['cdb_version'] not in cdb_versions:
        abort(422, 'API version must be one of: {}'.format(cdb_versions))

    if data['cdb_version'] == '1':
        if data['procurementMethodType'] == 'dgfInsider':
            if 'steps' not in data:
                abort(400, "Steps value wasn\'t found in request")
            if str(data['steps']).isdigit() is False:
                abort(400, 'Steps value must be integer')
            if int(data["steps"]) not in dgf_insider_steps:
                abort(422, 'Steps value must be between one of {}'.format(dgf_insider_steps))

    list_of_platform_urls = core.get_list_of_platform_urls(2)
    if data['platform_host'] not in list_of_platform_urls:
        abort(422, 'Platform must be one of: {}'.format(list_of_platform_urls))

    if int(data['accelerator']) < 30:
        if data['auctionStatus'] != 'active.tendering':
            abort(422, 'Accelerator value can be less than 30 for "active.tendering" status only')

    valid_data['min_number_of_qualified_bids'] = 2
    if 'minNumberOfQualifiedBids' in data:
        if data['minNumberOfQualifiedBids'] == '1':
            valid_data['min_number_of_qualified_bids'] = 1
        else:
            abort(422, 'minNumberOfQualifiedBids value must de "1" or empty')

    for field in data:
        if field != 'number_of_bids':
            valid_data[field] = data[field]

    if 'skip_auction' in data:
        valid_data['skip_auction'] = '(mode:no-auction)'
    else:
        valid_data['skip_auction'] = ''

    if 'steps' not in data:
        valid_data['steps'] = 0
    else:
        valid_data['steps'] = int(data['steps'])

    valid_data['rent'] = False
    if 'rent' in data:
        valid_data['rent'] = True

    return valid_data


def validator_add_auction_bid_to_company(bid_id, data):
    list_of_bids = BidsAuction.query.all()
    list_bid = []
    for tid in range(len(list_of_bids)):
        list_bid.append(list_of_bids[tid].bid_id)
    if bid_id not in list_bid:
        abort(404, 'Bid id was not found in database')

    if 'company-id' not in data:
        abort(400, 'Company UID was not found in request')

    if str(data['company-id']).isdigit() is False:
        abort(400, 'Company UID must be integer')

    if int(data['company-id']) == 0:
        abort(422, 'Company id can\'t be 0')

    return data


def validator_if_auction_id_short_in_db(auction_id_short):
    list_of_auctions = Auctions.query.all()
    list_tid = []
    for tid in range(len(list_of_auctions)):
        db.session.remove()
        list_tid.append(list_of_auctions[tid].auction_id_short)
    if auction_id_short not in list_tid:
        abort(404, alert.error_404_not_found('alert_error_404_no_auction_id'))
    return True
