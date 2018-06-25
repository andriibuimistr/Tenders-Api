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

    print('id long: ' + asset_id_long, 'token: ' + asset_token, 'id short: ' + asset_id_short, 'status: ' + asset_status)