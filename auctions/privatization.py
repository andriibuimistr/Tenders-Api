# -*- coding: utf-8 -*-
from cdb_requests import *
from auctions.data_for_privatization import *
import time
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

    lot = Privatization(entity='lot')
    json_lot = generate_lot_json(asset_id_long, 1440)
    lot_publish = lot.publish_lot(json_lot)

    lot_id_long = lot_publish.json()['data']['id']
    lot_token = lot_publish.json()['access']['token']
    lot_id_short = lot_publish.json()['data']['lotID']
    lot_transfer = lot_publish.json()['access']['transfer']

    lot_to_composing = lot.lot_to_composing(lot_id_long, lot_token)

    lot_status = lot_to_composing.json()['data']['status']

    # print('id long: ' + asset_id_long, 'token: ' + asset_token, 'id short: ' + asset_id_short, 'status: ' + asset_status)
    print('id long: ' + lot_id_long, 'token: ' + lot_token, 'transfer: ' + lot_transfer, 'id short: ' + lot_id_short, 'status: ' + lot_status)
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
        print('Attempt: {}'.format(attempts))
        status = lot.get_lot_info(lot_id_long).json()['data']['status']
        print('Status: '.format(status))
        if status == 'active.auction':
            break
        else:
            time.sleep(30)
            continue
    if attempts == 20:
        return False
    print(lot.get_lot_info(lot_id_long).json())
    rectification = lot.get_lot_info(lot_id_long).json()['data']['rectificationPeriod']['endDate']  # get tender period end date
    waiting_time = count_waiting_time(rectification, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_utc_now), None, 'lots')
    if waiting_time > 0:  # delete in the future
        time_counter(waiting_time, 'Check if rectificationPeriod is finished')
    auction = Privatization().activate_auction(lot_auctions[0]['id'], lot_token)
    print(auction.json())






create_asset(2)
