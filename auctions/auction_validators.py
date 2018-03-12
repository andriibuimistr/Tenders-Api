# -*- coding: utf-8 -*-
from auction_additional_data import create_auction_required_fields, auction_status_to_create, cdb_versions, auction_procurement_method_types
from flask import abort
import refresh


def validator_create_auction(data):
    for field in range(len(create_auction_required_fields)):
        if create_auction_required_fields[field] not in data:
            abort(400, "Field '{}' is required. List of required fields: {}".format(create_auction_required_fields[field], create_auction_required_fields))

    if str(data['number_of_items']).isdigit() is False:
        abort(400, 'Number of items must be integer')
    if 1 > int(data['number_of_items']) or int(data['number_of_items']) > 20:
        abort(422, 'Number of items must be between 1 and 20')

    if str(data["number_of_bids"]).isdigit() is False:
        abort(400, 'Number of bids must be integer')
    if 0 > int(data["number_of_bids"]) or int(data["number_of_bids"]) > 10:
        abort(422, 'Number of bids must be between 0 and 10')

    if str(data['accelerator']).isdigit() is False:
        abort(400, 'Accelerator must be integer')
    if 1 > int(data['accelerator']) or int(data['accelerator']) > 30000:
        abort(422, 'Accelerator must be between 1 and 30000')

    if str(data['company_id']).isdigit() is False:
        abort(400, 'Company ID must be integer')
    if int(data['company_id']) == 0:
        abort(422, 'Company id can\'t be 0')

    if data['auctionStatus'] not in auction_status_to_create:
        abort(422, 'Tender status must be one of: {}'.format(auction_status_to_create))

    if data['cdb_version'] not in cdb_versions:
        abort(422, 'API version must be one of: {}'.format(cdb_versions))

    list_of_platform_urls = refresh.get_list_of_platform_urls(2)
    if data['platform_host'] not in list_of_platform_urls:
        abort(422, 'Platform must be one of: {}'.format(list_of_platform_urls))

    if 'rent' in data:
        if data['rent'] != '1':
            abort(422, 'Rent value must de "1" or empty')

    if 'minNumberOfQualifiedBids' in data:
        if data['minNumberOfQualifiedBids'] != '1':
            abort(422, 'minNumberOfQualifiedBids value must de "1" or empty')

    if data['procurementMethodType'] not in auction_procurement_method_types:
        abort(422, 'procurementMethodType must be one of: {}'.format(auction_procurement_method_types))

    if int(data['accelerator']) < 30:
        if data['auctionStatus'] != 'active.tendering':
            abort(422, 'Accelerator value can be less than 30 for "active.tendering" status only')

    return True
