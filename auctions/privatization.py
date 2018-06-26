# -*- coding: utf-8 -*-
from cdb_requests import *
from auctions.data_for_privatization import *
import time


def create_asset(items):

    json_asset = generate_asset_json(items)

    asset = Privatization('asset')
    asset_publish = asset.publish_asset(json_asset)

    asset_id_long = asset_publish.json()['data']['id']
    asset_token = asset_publish.json()['access']['token']
    asset_id_short = asset_publish.json()['data']['assetID']

    time.sleep(1)
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
    print('id long: ' + lot_id_long, 'token: ' + lot_token, 'transfer: ' + lot_transfer, 'id short: ' + lot_id_short, 'status: ' + lot_status)
    print(lot_publish.json())

    auctions = lot_publish.json()['data']['auctions']
    for auction in range(len(auctions)):
        auction_id_long = auctions[auction]['id']
        patched_auction = lot.patch_lot_auction(lot_id_long, lot_token, fill_auction_data(auction + 1, accelerator=1440, lot_accelerator=1440), auction_id_long)
        print(patched_auction.json())

    lot_to_verification = lot.lot_to_verification(lot_id_long, lot_token)

    print(lot_to_verification.json())


create_asset(2)
