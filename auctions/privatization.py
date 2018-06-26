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
    json_lot = generate_lot_json(asset_id_long)
    lot_publish = lot.publish_lot(json_lot)

    lot_id_long = lot_publish.json()['data']['id']
    lot_token = lot_publish.json()['access']['token']
    lot_id_short = lot_publish.json()['data']['assetID']
    lot_transfer = lot_publish.json()['data']['assetID']

    # asset_status = asset_activate.json()['data']['status']

    print('id long: ' + asset_id_long, 'token: ' + asset_token, 'id short: ' + asset_id_short, 'status: ' + asset_status)
    print('id long: ' + lot_id_long, 'token: ' + lot_token, 'transfer: ' + lot_transfer, 'id short: ' + lot_id_short, 'status: ' + asset_status)


create_asset(2)
