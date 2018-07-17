# -*- coding: utf-8 -*-
from auctions.data_for_privatization import *
from config import kiev_now
from core import *


def create_asset(items):
    json_asset = generate_asset_json(items, accelerator=1)

    asset = Privatization('asset')
    asset_publish = asset.publish_asset(json_asset)

    asset_id_long = asset_publish.json()['data']['id']
    asset_token = asset_publish.json()['access']['token']
    # asset_id_short = asset_publish.json()['data']['assetID']

    asset.activate_asset(asset_id_long, asset_token)

    lot = Privatization('lot')
    json_lot = generate_lot_json(asset_id_long, 1440)
    lot_publish = lot.publish_lot(json_lot)

    lot_id_long = lot_publish.json()['data']['id']
    lot_token = lot_publish.json()['access']['token']
    # lot_id_short = lot_publish.json()['data']['lotID']
    lot_transfer = lot_publish.json()['access']['transfer']

    lot.lot_to_composing(lot_id_long, lot_token)

    lot_auctions = lot_publish.json()['data']['auctions']
    for auction in range(len(lot_auctions)):
        auction_id_long = lot_auctions[auction]['id']
        index = auction + 1
        lot.patch_lot_auction(lot_id_long, lot_token, fill_auction_data(auction + 1, accelerator=1440, lot_accelerator=1440), auction_id_long, index)

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

    au_id_long = lot.get_lot_info(lot_id_long).json()['data']['auctions'][0]['relatedProcessID']
    transfer = Privatization('transfer').create_transfer().json()
    print(transfer)
    json_of_transfer = {"data": {
                                "id": transfer['data']['id'],
                                "transfer": lot_transfer
    }}
    Privatization().change_auction_ownership(au_id_long, json_of_transfer).json()
    activate_auction = Privatization().activate_auction_privatization(au_id_long, transfer['access']['token'])
    print(activate_auction.json())
    print('c\'est fini')


create_asset(2)
