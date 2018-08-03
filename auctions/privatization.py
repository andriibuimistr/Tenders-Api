# -*- coding: utf-8 -*-
from auctions.data_for_privatization import *
from core import *
from auction import *


def create_privatization(ac_request, session):
    data = ac_request
    # def create_asset(ac_request, session):
    # data = auction_validators.validator_create_privatization(pr_request)  # validator of request data
    number_of_items = int(data['number_of_items'])
    accelerator_asset = int(data['acceleratorAsset'])
    accelerator_lot = int(data['acceleratorLot'])
    accelerator = int(data['accelerator'])
    company_id = int(data['company_id'])
    platform_host = data['platform_host']
    received_auction_status = data['auctionStatus']
    number_of_bids = int(data['number_of_bids'])
    # skip_auction = data['skip_auction']!!!

    decision = generate_decision()
    json_asset = generate_asset_json(number_of_items, asset_accelerator=accelerator_asset, decision=decision)

    asset = Privatization('asset')
    asset_publish = asset.publish_asset(json_asset)

    asset_id_long = asset_publish.json()['data']['id']
    asset_token = asset_publish.json()['access']['token']
    # asset_id_short = asset_publish.json()['data']['assetID']
    asset.add_decisions_to_asset(asset_id_long, asset_token, decision)

    asset.activate_asset(asset_id_long, asset_token)

    lot = Privatization('lot')
    json_lot = generate_lot_json(asset_id_long, 1440)
    lot_publish = lot.publish_lot(json_lot)

    lot_id_long = lot_publish.json()['data']['id']
    lot_token = lot_publish.json()['access']['token']
    # lot_id_short = lot_publish.json()['data']['lotID']
    lot_transfer = lot_publish.json()['access']['transfer']
    print(lot_id_long)

    lot.lot_to_composing(lot_id_long, lot_token)

    lot_auctions = lot_publish.json()['data']['auctions']  # Get list of auctions from lot
    for auction in range(len(lot_auctions)):  # Fill auctions data in lot
        auction_id_long = lot_auctions[auction]['id']
        index = auction + 1
        lot.patch_lot_auction(lot_id_long, lot_token, fill_auction_data(index, lot_accelerator=accelerator_lot, auction_accelerator=accelerator), auction_id_long, index)

    lot.add_decision_to_lot(lot_id_long, lot_token, decision)
    lot.lot_to_verification(lot_id_long, lot_token)

    time_counter(60, '"Check lot pending status"')
    attempts = 0
    for x in range(20):
        attempts += 1
        print('Check pending status. Attempt: {}'.format(attempts))
        status = lot.get_lot_info(lot_id_long).json()['data']['status']
        print('Status: {}'.format(status))
        if status == 'pending':
            break
        else:
            time.sleep(30)
            continue
    if attempts == 20:
        return False

    rectification = lot.get_lot_info(lot_id_long).json()['data']['rectificationPeriod']['endDate']  # get tender period end date
    waiting_time = count_waiting_time(rectification, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_now), None, 'lots')
    if waiting_time > 0:  # delete in the future
        time_counter(waiting_time, 'Check if rectificationPeriod is finished')

    attempts = 0
    for x in range(20):
        attempts += 1
        print('Check active.auction status. Attempt: {}'.format(attempts))
        status = lot.get_lot_info(lot_id_long).json()['data']['status']
        print('Status: {}'.format(status))
        if status == 'active.auction':
            break
        else:
            time.sleep(30)
            continue
    if attempts == 20:
        return False

    au_id_long = lot.get_lot_info(lot_id_long).json()['data']['auctions'][0]['relatedProcessID']  # Get auction ID from lot
    transfer = Privatization('transfer').create_transfer().json()
    auction_token = transfer['access']['token']
    print(transfer)
    json_of_transfer = {"data": {
                                "id": transfer['data']['id'],
                                "transfer": lot_transfer
    }}
    Privatization().change_auction_ownership(au_id_long, json_of_transfer)
    activate_auction = Privatization().activate_auction_privatization(au_id_long, auction_token)
    auction_id_long = activate_auction.json()['data']['id']
    auction_id_short = activate_auction.json()['data']['auctionID']
    procurement_method_type = activate_auction.json()['data']['procurementMethodType']
    auction_status = activate_auction.json()['data']['status']

    auction_to_db(auction_id_long, auction_id_short, auction_token, procurement_method_type, auction_status, 1, cdb_version=2)  # add auction data to database
    add_auction_to_company = core.add_one_tender_company(company_id=company_id, company_platform_host=platform_host,
                                                         entity_id_long=auction_id_long, entity_token=auction_token, entity='auction')  # add auction to local database
    create_bids(cdb=2, auction_id_long=auction_id_long, procurement_method_type=procurement_method_type, number_of_bids=number_of_bids)  # make bids

    print('Long: {} Short: {}'.format(auction_id_long, auction_id_short))

    # Initial 'Response JSON' data
    response_json = dict()
    response_json['tender_to_company'] = add_auction_to_company[0], '{}{}{}'.format(platform_host, '/buyer/tender/view/', auction_id_short)
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


# create_privatization(items=2, bids=1, platform_host='http://eauction-dev.byustudio.in.ua', company=306, asset_accelerator=1, lot_accelerator=720, auction_accelerator=360)
