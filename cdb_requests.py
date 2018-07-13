# -*- coding: utf-8 -*-
from auctions.auction_data_for_requests import *
from tenders.tender_data_for_requests import *
from flask import abort
import os
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time
from datetime import datetime, timedelta
from pprint import pformat


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def save_log(code, body, resp_header, host, endpoint, method, request_name, entity, headers, json_request):
    now = datetime.now()
    path = os.path.join(ROOT_DIR, 'logs', entity, str(now.year), str(now.month), str(now.day), str(now.hour),
                        '{} {} {}.txt'.format(code, datetime.now().strftime("%d-%m-%Y %H-%M-%S"), request_name))
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    f = open(path, "w+")
    try:
        body = json.loads(body)
    except Exception as e:
        print e
        body = body
    f.write('{} {}{}\n\n{}\n\n{}\n\n{}\n\n{}'.format(method, host, endpoint, str(headers).replace(',', ',\n'),
                                                     pformat(json_request), str(resp_header).replace(',', ',\n'), pformat(body)))
    f.close()


# Send request to cdb
def request_to_cdb(headers, host, endpoint, method, json_request, request_name, entity, is_json=True):
    if is_json:
        json_request = json.dumps(json_request)
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            if method != 'GET':
                s.request("HEAD", "{}".format(host))
            r = requests.Request(method, "{}{}".format(host, endpoint),
                                 data=json_request,
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            resp.raise_for_status()
            if resp.status_code in [200, 201, 202]:
                print("{}: Success".format(request_name))
                print("       status code:  {}".format(resp.status_code))
                # save_log(resp.status_code, resp.content, resp.headers, host, endpoint, method, request_name, entity, headers, json_request)
                return resp
        except HTTPError as error:
            print("{}: Error".format(request_name))
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            save_log(error.response.status_code, resp.content, resp.headers, host, endpoint, method, request_name, entity, headers, json_request)
            time.sleep(1)
            if attempts >= 5:
                abort(error.response.status_code, resp.content)
        except ConnectionError as e:
            print 'Connection Exception'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                save_log(503, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
                abort(503, '{} error: {}'.format(request_name, e))
        except requests.exceptions.MissingSchema as e:
            print 'MissingSchema Exception'
            save_log(500, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
            abort(500, '{} error: {}'.format(request_name, e))
        except Exception as e:
            print 'General Exception'
            save_log(500, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
            abort(500, '{} error: {}'.format(request_name, e))


class TenderRequests(object):

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = tender_host_selector(cdb)[0]
        self.host_public = tender_host_selector(cdb)[1]
        self.ds_host = tender_ds_host_selector(cdb)
        self.entity = 'tenders'
        self.document = 'tender_documents'

    def publish_tender(self, json_tender):
        return request_to_cdb(tender_headers_request(self.cdb, json_tender), self.host, '', 'POST', json_tender, 'Publish tender', self.entity)

    def activate_tender(self, tender_id_long, token, procurement_method):
        json_tender_activation = json_activate_tender(procurement_method)
        return request_to_cdb(tender_headers_request(self.cdb, json_tender_activation), self.host, '/{}?acc_token={}'.format(tender_id_long, token),
                              'PATCH', json_tender_activation, 'Activate tender', self.entity)

    def get_tender_info(self, tender_id_long):
        return request_to_cdb(None, self.host_public, '/{}'.format(tender_id_long), 'GET', None, 'Get tender info', self.entity)

    def finish_first_stage(self, tender_id_long, token):
        return request_to_cdb(tender_headers_request(self.cdb, json_finish_first_stage), self.host, '/{}?acc_token={}'.format(tender_id_long, token),
                              'PATCH', json_finish_first_stage, 'Finish first stage', self.entity)

    def patch_second_stage(self, tender_id_long, token, json_patch_2nd_stage):
        return request_to_cdb(tender_headers_request(self.cdb, json_patch_2nd_stage), self.host, '/{}?acc_token={}'.format(tender_id_long, token),
                              'PATCH',  json_patch_2nd_stage, 'Patch 2nd stage', self.entity)

    def activate_2nd_stage(self, tender_id_long, token, procurement_method):
        json_tender_activation = json_activate_tender(procurement_method)
        return request_to_cdb(tender_headers_request(self.cdb, json_tender_activation), self.host, '/{}?acc_token={}'.format(tender_id_long, token),
                              'PATCH', json_tender_activation, 'Activate 2nd stage', self.entity)

    def get_2nd_stage_info(self, tender_id_long, token):
        return request_to_cdb(tender_headers_request(self.cdb, None), self.host, '/{}/credentials?acc_token={}'.format(tender_id_long, token),
                              'PATCH', None, 'Get 2nd stage info', self.entity)

    def approve_prequalification(self, tender_id_long, qualification_id, token, json_pq):
        return request_to_cdb(tender_headers_request(self.cdb, json_pq), self.host, '/{}/qualifications/{}?acc_token={}'.format(tender_id_long, qualification_id, token),
                              'PATCH', json_pq, 'Approve prequalification', self.entity)

    def finish_prequalification(self, tender_id_long, token):
        return request_to_cdb(tender_headers_request(self.cdb, json_finish_pq), self.host, '/{}?acc_token={}'.format(tender_id_long, token),
                              'PATCH', json_finish_pq, 'Finish prequalification', self.entity)

    def activate_award_contract(self, tender_id_long, entity, entity_id, token, activation_json, count):
        request_to_cdb(tender_headers_request(self.cdb, activation_json), self.host, '/{}/{}/{}?acc_token={}'.format(tender_id_long, entity, entity_id, token),
                       'PATCH', activation_json, 'Activate {} {}'.format(entity, count), self.entity)

    def add_supplier_limited(self, tender_id_long, token, add_supplier_json, supplier_number):
        return request_to_cdb(tender_headers_request(self.cdb, add_supplier_json), self.host, '/{}/awards?acc_token={}'.format(tender_id_long, token),
                              'POST', add_supplier_json, 'Add supplier {}'.format(supplier_number), self.entity)

    def make_tender_bid(self, tender_id_long, bid_json, bid_number):
        return request_to_cdb(tender_headers_request(self.cdb, bid_json), self.host, '/{}/bids'.format(tender_id_long),
                              'POST', bid_json, 'Publish bid {}'.format(bid_number), self.entity)

    def activate_tender_bid(self, tender_id_long, bid_id, bid_token, activate_bid_json, bid_number):
        return request_to_cdb(tender_headers_request(self.cdb, activate_bid_json), self.host, '/{}/bids/{}?acc_token={}'.format(tender_id_long, bid_id, bid_token),
                              'PATCH', activate_bid_json, 'Activate bid {}'.format(bid_number), self.entity)

    def get_list_of_tenders(self):
        return request_to_cdb(tender_headers_request(self.cdb, None), self.host_public, '', 'GET', None, 'Get list of tenders', self.entity)

    def get_bid_info(self, tender_id_long, bid_id, bid_token):
        return request_to_cdb(tender_headers_request(self.cdb, None), self.host, '/{}/bids/{}?acc_token={}'.format(tender_id_long, bid_id, bid_token),
                              'GET', None, 'Get bid info', self.entity)

    def add_tender_document_to_ds(self, document_data):
        return request_to_cdb(tender_headers_add_document_ds, self.ds_host, '', 'POST', document_data, 'Add document to DS (tenders)', self.document, False)

    def add_document_from_ds_to_tender(self, tender_id_long, tender_token, json_with_document, message):
        return request_to_cdb(tender_headers_patch_document_ds, self.host, "/{}/documents?acc_token={}".format(tender_id_long, tender_token), 'POST', json_with_document, message, self.document)

    def add_document_from_ds_to_tender_bid(self, tender_id_long, bid_id, doc_type_url, bid_token, json_with_document, message):
        return request_to_cdb(tender_headers_patch_document_ds, self.host, "/{}/bids/{}/{}?acc_token={}".format(tender_id_long, bid_id, doc_type_url, bid_token), 'POST', json_with_document, message, self.document)

    def add_document_from_ds_to_entity(self, tender_id_long, entity_id, tender_token, json_with_document, message, entity):
        return request_to_cdb(tender_headers_patch_document_ds, self.host, "/{}/{}/{}/documents?acc_token={}".format(tender_id_long, entity, entity_id, tender_token), 'POST', json_with_document, message, self.document)


class AuctionRequests(object):

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = auction_host_selector(cdb)
        self.__entity = 'auctions'

    def publish_auction(self, json_auction):
        return request_to_cdb(auction_headers_request(self.cdb, json_auction), self.host, '', 'POST', json_auction, 'Publish auction', self.__entity)

    def activate_auction(self, auction_id_long, token):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_active_tendering), self.host, '/{}?acc_token={}'.format(auction_id_long, token),
                              'PATCH', json_status_active_tendering, 'Activate auction', self.__entity)

    def make_bid_auction(self, auction_id_long, json_bid):
        return request_to_cdb(auction_headers_request(self.cdb, json_bid), self.host, '/{}/bids'.format(auction_id_long),
                              'POST', json_bid, 'Publish auction bid', self.__entity)

    def activate_auction_bid(self, auction_id_long, bid_id, bid_token):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_active), self.host, '/{}/bids/{}?acc_token={}'.format(auction_id_long, bid_id, bid_token),
                              'PATCH', json_status_active, 'Activate auction bid', self.__entity)

    def get_auction_info(self, auction_id_long):
        return request_to_cdb(None, self.host, '/{}'.format(auction_id_long), 'GET', None, 'Get auction info', self.__entity)

    def get_list_of_auctions(self):
        endpoint = ((datetime.now() - timedelta(minutes=60)).strftime('?offset=%Y-%m-%dT%Hx%Mx%S.104183y03x00&mode=_all_')).replace('x', '%3A').replace('y', '%2B')
        return request_to_cdb(tender_headers_request(self.cdb, None), self.host, endpoint, 'GET', None, 'Get list of auctions', self.__entity)

    def change_auction_ownership(self, auction_id_long, json_of_transfer):
        return request_to_cdb(auction_headers_request(self.cdb, json_of_transfer), self.host, '/{}/ownership'.format(auction_id_long),
                              'POST', json_of_transfer, 'Change auction ownership', self.__entity)

    def activate_auction_privatization(self, auction_id_long, token):
        return request_to_cdb(auction_headers_request(self.cdb, json_activate_auction_p(token)), self.host, '/{}'.format(auction_id_long),
                              'PATCH', json_activate_auction_p(token), 'Activate auction privatization', self.__entity)


class Privatization(AuctionRequests):

    def __init__(self, entity=None):
        self.entity = entity
        self.host_p = privatization_host_selector(self.entity)
        super(Privatization, self).__init__(2)

    def publish_asset(self, json_asset):
        return request_to_cdb(auction_headers_request(self.cdb, json_asset), self.host_p, '', 'POST', json_asset, 'Publish asset', self.entity)

    def activate_asset(self, asset_id_long, token):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_pending), self.host_p, '/{}?acc_token={}'.format(asset_id_long, token),
                              'PATCH', json_status_pending, 'Activate asset', self.entity)

    def get_asset_info(self, asset_id_long):
        return request_to_cdb(None, self.host_p, '/{}'.format(asset_id_long), 'GET', None, 'Get asset info', self.entity)

    def publish_lot(self, json_lot):
        return request_to_cdb(auction_headers_request(self.cdb, json_lot), self.host_p, '', 'POST', json_lot, 'Publish lot', self.entity)

    def lot_to_composing(self, lot_id_long, token):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_composing), self.host_p, '/{}?acc_token={}'.format(lot_id_long, token),
                              'PATCH', json_status_composing, 'Lot to composing', self.entity)

    def lot_to_verification(self, lot_id_long, token):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_composing), self.host_p, '/{}?acc_token={}'.format(lot_id_long, token),
                              'PATCH', json_status_verification, 'Lot to verification', self.entity)

    def get_lot_info(self, lot_id_long):
        return request_to_cdb(None, self.host_p, '/{}'.format(lot_id_long), 'GET', None, 'Get lot info', self.entity)

    def patch_lot_auction(self, lot_id_long, token, json_path_auction, auction_id_long, index):
        return request_to_cdb(auction_headers_request(self.cdb, json_status_composing, token), self.host_p, '/{}/auctions/{}'.format(lot_id_long, auction_id_long),
                              'PATCH', json_path_auction, 'Patch auction {} in lot'.format(index), self.entity)

    def get_list_of_lots(self):
        return request_to_cdb(tender_headers_request(self.cdb, None), self.host_p, '', 'GET', None, 'Get list of lots', self.entity)

    def create_transfer(self):
        return request_to_cdb(auction_headers_request(self.cdb, transfer_json), self.host_p, '', 'POST', transfer_json, 'Create transfer', self.entity)


class Monitoring(object):

    def __init__(self, cdb):
        self.host = monitoring_host
        self.headers = monitoring_headers
        self.entity = 'monitoring'
        self.tenders_host = tender_host_selector(cdb)[0]
        self.cdb = cdb

    def publish_monitoring(self, json_monitoring):
        return request_to_cdb(self.headers, self.host, '', 'POST', json_monitoring, 'Publish monitoring', self.entity)

    def patch_monitoring(self, monitoring_id, json_body, message):
        return request_to_cdb(self.headers, self.host, '/{}'.format(monitoring_id), 'PATCH', json_body, message, self.entity)

    def add_post(self, monitoring_id, post_json):
        return request_to_cdb(self.headers, self.host, '/{}/posts'.format(monitoring_id), 'POST', post_json, 'Add post to monitoring', self.entity)
