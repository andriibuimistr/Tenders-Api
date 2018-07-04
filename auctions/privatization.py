# -*- coding: utf-8 -*-
from auctions.data_for_privatization import *
from core import *


def create_asset(items):

    json_asset = generate_asset_json(items)

    asset = Privatization('asset')
    asset_publish = asset.publish_asset(json_asset)

    asset_id_long = asset_publish.json()['data']['id']
    asset_token = asset_publish.json()['access']['token']
    asset_id_short = asset_publish.json()['data']['assetID']

    asset_activate = asset.activate_asset(asset_id_long, asset_token)
    asset_status = asset_activate.json()['data']['status']

    lot = Privatization('lot')
    json_lot = generate_lot_json(asset_id_long, 1440)
    lot_publish = lot.publish_lot(json_lot)

    lot_id_long = lot_publish.json()['data']['id']
    lot_token = lot_publish.json()['access']['token']
    lot_id_short = lot_publish.json()['data']['lotID']
    lot_transfer = lot_publish.json()['access']['transfer']

    lot_to_composing = lot.lot_to_composing(lot_id_long, lot_token)

    lot_status = lot_to_composing.json()['data']['status']

    # print('id long: ' + asset_id_long, 'token: ' + asset_token, 'id short: ' + asset_id_short, 'status: ' + asset_status)
    # print('id long: ' + lot_id_long, 'token: ' + lot_token, 'transfer: ' + lot_transfer, 'id short: ' + lot_id_short, 'status: ' + lot_status)
    # print(lot_publish.json())

    lot_auctions = lot_publish.json()['data']['auctions']
    for auction in range(len(lot_auctions)):
        auction_id_long = lot_auctions[auction]['id']
        index = auction + 1
        patched_auction = lot.patch_lot_auction(lot_id_long, lot_token, fill_auction_data(index, accelerator=1440, lot_accelerator=1440), auction_id_long, index)
        # print(patched_auction.json())

    lot_to_verification = lot.lot_to_verification(lot_id_long, lot_token)
    # print(lot_to_verification.json())

    print('Sleep 60 sec.')
    time.sleep(60)

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
    # print(lot.get_lot_info(lot_id_long).json())
    rectification = lot.get_lot_info(lot_id_long).json()['data']['rectificationPeriod']['endDate']  # get tender period end date
    waiting_time = count_waiting_time(rectification, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_utc_now), None, 'lots')
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

    # print(lot_auctions)
    first_auction_short_id = lot.get_lot_info(lot_id_long).json()['data']['auctions'][0]['auctionID']

    # get_list_number = 0
    # for attempt in range(10):
    # list_of_all_auctions = Privatization().get_list_of_auctions().json()['data']
    # get_list_number += 1
    # print('Get list of auctions. Attempt: {}'.format(get_list_number))
    time.sleep(60)
    auction_number = 0
    # for x in range(len(list_of_all_auctions)):
    #     auction_number += 1
    #     print('Auction number: {}'.format(auction_number))
    au_id_long = lot.get_lot_info(lot_id_long).json()['data']['auctions'][0]['relatedProcessID']
        # auction_id_short = Privatization().get_auction_info(au_id_long).json()['data']['auctionID']
        # if first_auction_short_id == auction_id_short:
    transfer = Privatization('transfer').create_transfer().json()
    print(transfer)
    json_of_transfer = {"data": {
                                "id": transfer['data']['id'],
                                "transfer": lot_transfer
    }}
    change_ownership = Privatization().change_auction_ownership(au_id_long, json_of_transfer).json()
            # print(change_ownership)

    activate_auction = Privatization().activate_auction_privatization(au_id_long, transfer['access']['token'])
    print(activate_auction.json())
            # break

    print('c\'est fini')


create_asset(2)
