# -*- coding: utf-8 -*-
from data_for_requests import *
from flask import abort
import os
import json
import requests
from requests.exceptions import ConnectionError, HTTPError
import time
from datetime import datetime, timedelta
from pprint import pformat
from config import ROOT_DIR
from data_for_requests import auction_host_selector, auction_headers_request, privatization_host_selector, transfer_json, json_activate_auction_p


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
def request_to_cdb(headers, host, method, json_request, request_name, entity, endpoint='', is_json=True, files=None):
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
                                 files=files)
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
                abort(error.response.status_code, {'response_error': resp.content})
        except ConnectionError as e:
            print 'Connection Exception'
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                save_log(503, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
                abort(503, {'response_error': '{} error: {}'.format(request_name, e)})
        except requests.exceptions.MissingSchema as e:
            print 'MissingSchema Exception'
            save_log(500, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
            abort(500, {'response_error': '{} error: {}'.format(request_name, e)})
        except Exception as e:
            print 'General Exception'
            save_log(500, str(e), 'No header', host, endpoint, method, request_name, entity, headers, json_request)
            abort(500, {'response_error': '{} error: {}'.format(request_name, e)})


class TenderRequests(object):

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = tender_host_selector(cdb)[0]
        self.host_public = tender_host_selector(cdb)[1]
        self.ds_host = tender_ds_host_selector(cdb)
        self.entity = 'tenders'
        self.document = 'tender_documents'

    def publish_tender(self, json_tender):
        return request_to_cdb(headers=tender_headers_request(json_tender),
                              host=self.host,
                              method='POST',
                              json_request=json_tender,
                              request_name='Publish tender',
                              entity=self.entity)

    def activate_tender(self, tender_id_long, token, procurement_method):
        json_tender_activation = json_activate_tender(procurement_method)
        return request_to_cdb(headers=tender_headers_request(json_tender_activation),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=json_tender_activation,
                              request_name='Activate tender',
                              entity=self.entity)

    def get_tender_info(self, tender_id_long):
        return request_to_cdb(headers=None,
                              host=self.host_public,
                              endpoint='/{}'.format(tender_id_long),
                              method='GET',
                              json_request=None,
                              request_name='Get tender info',
                              entity=self.entity)

    def finish_first_stage(self, tender_id_long, token):
        return request_to_cdb(headers=tender_headers_request(json_status('active.stage2.waiting')),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=json_status('active.stage2.waiting'),
                              request_name='Finish first stage',
                              entity=self.entity)

    def patch_second_stage(self, tender_id_long, token, json_patch_2nd_stage):
        return request_to_cdb(headers=tender_headers_request(json_patch_2nd_stage),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=json_patch_2nd_stage,
                              request_name='Patch 2nd stage',
                              entity=self.entity)

    def activate_2nd_stage(self, tender_id_long, token, procurement_method):
        json_tender_activation = json_activate_tender(procurement_method)
        return request_to_cdb(headers=tender_headers_request(json_tender_activation),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=json_tender_activation,
                              request_name='Activate 2nd stage',
                              entity=self.entity)

    def get_2nd_stage_info(self, tender_id_long, token):
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host,
                              endpoint='/{}/credentials?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=None,
                              request_name='Get 2nd stage info',
                              entity=self.entity)

    def approve_prequalification(self, tender_id_long, qualification_id, token, json_pq):
        return request_to_cdb(headers=tender_headers_request(json_pq),
                              host=self.host,
                              endpoint='/{}/qualifications/{}?acc_token={}'.format(tender_id_long, qualification_id, token),
                              method='PATCH',
                              json_request=json_pq,
                              request_name='Approve prequalification',
                              entity=self.entity)

    def finish_prequalification(self, tender_id_long, token):
        return request_to_cdb(headers=tender_headers_request(json_status('active.pre-qualification.stand-still')),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(tender_id_long, token),
                              method='PATCH',
                              json_request=json_status('active.pre-qualification.stand-still'),
                              request_name='Finish prequalification',
                              entity=self.entity)

    def activate_award_contract(self, tender_id_long, entity, entity_id, token, activation_json, count):
        return request_to_cdb(headers=tender_headers_request(activation_json),
                              host=self.host,
                              endpoint='/{}/{}/{}?acc_token={}'.format(tender_id_long, entity, entity_id, token),
                              method='PATCH',
                              json_request=activation_json,
                              request_name='Activate {} {}'.format(entity, count),
                              entity=self.entity)

    def add_supplier_limited(self, tender_id_long, token, add_supplier_json, supplier_number):
        return request_to_cdb(headers=tender_headers_request(add_supplier_json),
                              host=self.host,
                              endpoint='/{}/awards?acc_token={}'.format(tender_id_long, token),
                              method='POST',
                              json_request=add_supplier_json,
                              request_name='Add supplier {}'.format(supplier_number),
                              entity=self.entity)

    def make_tender_bid(self, tender_id_long, bid_json, bid_number):
        return request_to_cdb(headers=tender_headers_request(bid_json),
                              host=self.host,
                              endpoint='/{}/bids'.format(tender_id_long),
                              method='POST',
                              json_request=bid_json,
                              request_name='Publish bid {}'.format(bid_number),
                              entity=self.entity)

    def activate_tender_bid(self, tender_id_long, bid_id, bid_token, activate_bid_json, bid_number):
        return request_to_cdb(headers=tender_headers_request(activate_bid_json),
                              host=self.host,
                              endpoint='/{}/bids/{}?acc_token={}'.format(tender_id_long, bid_id, bid_token),
                              method='PATCH',
                              json_request=activate_bid_json,
                              request_name='Activate bid {}'.format(bid_number),
                              entity=self.entity)

    def get_list_of_tenders(self):
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host_public,
                              method='GET',
                              json_request=None,
                              request_name='Get list of tenders',
                              entity=self.entity)

    def get_bid_info(self, tender_id_long, bid_id, bid_token):
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host,
                              endpoint='/{}/bids/{}?acc_token={}'.format(tender_id_long, bid_id, bid_token),
                              method='GET',
                              json_request=None,
                              request_name='Get bid info',
                              entity=self.entity)

    def add_tender_document_to_ds(self, files):
        return request_to_cdb(headers=tender_headers_add_document_ds,
                              host=self.ds_host,
                              method='POST',
                              json_request=None,
                              request_name='Add document to DS (tenders)',
                              entity=self.document,
                              is_json=False,
                              files=files)

    def add_document_from_ds_to_tender(self, tender_id_long, tender_token, json_with_document, message):
        return request_to_cdb(headers=tender_headers_patch_document_ds,
                              host=self.host,
                              endpoint="/{}/documents?acc_token={}".format(tender_id_long, tender_token),
                              method='POST',
                              json_request=json_with_document,
                              request_name=message,
                              entity=self.document)

    def add_document_from_ds_to_tender_bid(self, tender_id_long, bid_id, doc_type_url, bid_token, json_with_document, message):
        return request_to_cdb(headers=tender_headers_patch_document_ds,
                              host=self.host,
                              endpoint="/{}/bids/{}/{}?acc_token={}".format(tender_id_long, bid_id, doc_type_url, bid_token),
                              method='POST',
                              json_request=json_with_document,
                              request_name=message,
                              entity=self.document)

    def add_document_from_ds_to_entity(self, tender_id_long, entity_id, tender_token, json_with_document, message, entity):
        return request_to_cdb(headers=tender_headers_patch_document_ds,
                              host=self.host,
                              endpoint="/{}/{}/{}/documents?acc_token={}".format(tender_id_long, entity, entity_id, tender_token),
                              method='POST',
                              json_request=json_with_document,
                              request_name=message,
                              entity=self.document)


class AuctionRequests(object):

    def __init__(self, cdb):
        self.cdb = cdb
        self.host = auction_host_selector(cdb)
        self.__entity = 'auctions'

    def publish_auction(self, json_auction):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_auction),
                              host=self.host,
                              method='POST',
                              json_request=json_auction,
                              request_name='Publish auction',
                              entity=self.__entity)

    def activate_auction(self, auction_id_long, token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_status('active.tendering')),
                              host=self.host,
                              endpoint='/{}?acc_token={}'.format(auction_id_long, token),
                              method='PATCH',
                              json_request=json_status('active.tendering'),
                              request_name='Activate auction',
                              entity=self.__entity)

    def make_bid_auction(self, auction_id_long, json_bid):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_bid),
                              host=self.host,
                              endpoint='/{}/bids'.format(auction_id_long),
                              method='POST',
                              json_request=json_bid,
                              request_name='Publish auction bid',
                              entity=self.__entity)

    def activate_auction_bid(self, auction_id_long, bid_id, bid_token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_status('active')),
                              host=self.host,
                              endpoint='/{}/bids/{}?acc_token={}'.format(auction_id_long, bid_id, bid_token),
                              method='PATCH',
                              json_request=json_status('active'),
                              request_name='Activate auction bid',
                              entity=self.__entity)

    def get_auction_info(self, auction_id_long):
        return request_to_cdb(headers=None,
                              host=self.host,
                              endpoint='/{}'.format(auction_id_long),
                              method='GET',
                              json_request=None,
                              request_name='Get auction info',
                              entity=self.__entity)

    def get_list_of_auctions(self):
        endpoint = ((datetime.now() - timedelta(minutes=60)).strftime('?offset=%Y-%m-%dT%Hx%Mx%S.104183y03x00&mode=_all_')).replace('x', '%3A').replace('y', '%2B')
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host,
                              endpoint=endpoint,
                              method='GET',
                              json_request=None,
                              request_name='Get list of auctions',
                              entity=self.__entity)

    def change_auction_ownership(self, auction_id_long, json_of_transfer):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_of_transfer),
                              host=self.host,
                              endpoint='/{}/ownership'.format(auction_id_long),
                              method='POST',
                              json_request=json_of_transfer,
                              request_name='Change auction ownership',
                              entity=self.__entity)

    def activate_auction_privatization(self, auction_id_long, token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_activate_auction_p(token)),
                              host=self.host,
                              endpoint='/{}'.format(auction_id_long),
                              method='PATCH',
                              json_request=json_activate_auction_p(token),
                              request_name='Activate auction privatization',
                              entity=self.__entity)


class Privatization(AuctionRequests):

    def __init__(self, entity=None):
        self.entity = entity
        self.host_p = privatization_host_selector(self.entity)
        super(Privatization, self).__init__(2)

    def publish_asset(self, json_asset):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_asset),
                              host=self.host_p,
                              method='POST',
                              json_request=json_asset,
                              request_name='Publish asset',
                              entity=self.entity)

    def activate_asset(self, asset_id_long, token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_status('pending')),
                              host=self.host_p,
                              endpoint='/{}?acc_token={}'.format(asset_id_long, token),
                              method='PATCH',
                              json_request=json_status('pending'),
                              request_name='Activate asset',
                              entity=self.entity)

    def add_decisions_to_asset(self, asset_id_long, token, decision_json):
        return request_to_cdb(headers=auction_headers_request(self.cdb, decision_json),
                              host=self.host_p,
                              endpoint='/{}/decisions?acc_token={}'.format(asset_id_long, token),
                              method='POST',
                              json_request=decision_json,
                              request_name='Add decision to asset',
                              entity=self.entity)

    def get_asset_info(self, asset_id_long):
        return request_to_cdb(headers=None,
                              host=self.host_p,
                              endpoint='/{}'.format(asset_id_long),
                              method='GET',
                              json_request=None,
                              request_name='Get asset info',
                              entity=self.entity)

    def publish_lot(self, json_lot):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_lot),
                              host=self.host_p,
                              method='POST',
                              json_request=json_lot,
                              request_name='Publish lot',
                              entity=self.entity)

    def lot_to_composing(self, lot_id_long, token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_status('composing')),
                              host=self.host_p,
                              endpoint='/{}?acc_token={}'.format(lot_id_long, token),
                              method='PATCH',
                              json_request=json_status('composing'),
                              request_name='Lot to composing',
                              entity=self.entity)

    def add_decision_to_lot(self, lot_id_long, token, decision_json):
        return request_to_cdb(headers=auction_headers_request(self.cdb, decision_json),
                              host=self.host_p,
                              endpoint='/{}/decisions?acc_token={}'.format(lot_id_long, token),
                              method='POST',
                              json_request=decision_json,
                              request_name='Add decision to lot',
                              entity=self.entity)

    def lot_to_verification(self, lot_id_long, token):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_status('verification')),
                              host=self.host_p,
                              endpoint='/{}?acc_token={}'.format(lot_id_long, token),
                              method='PATCH',
                              json_request=json_status('verification'),
                              request_name='Lot to verification',
                              entity=self.entity)

    def get_lot_info(self, lot_id_long):
        return request_to_cdb(headers=None,
                              host=self.host_p,
                              endpoint='/{}'.format(lot_id_long),
                              method='GET',
                              json_request=None,
                              request_name='Get lot info',
                              entity=self.entity)

    def patch_lot_auction(self, lot_id_long, token, json_patch_auction, auction_id_long, index):
        return request_to_cdb(headers=auction_headers_request(self.cdb, json_patch_auction, token),
                              host=self.host_p,
                              endpoint='/{}/auctions/{}'.format(lot_id_long, auction_id_long),
                              method='PATCH',
                              json_request=json_patch_auction,
                              request_name='Patch auction {} in lot'.format(index),
                              entity=self.entity)

    def get_list_of_lots(self):
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host_p,
                              method='GET',
                              json_request=None,
                              request_name='Get list of lots',
                              entity=self.entity)

    def create_transfer(self):
        return request_to_cdb(headers=auction_headers_request(self.cdb, transfer_json),
                              host=self.host_p,
                              method='POST',
                              json_request=transfer_json,
                              request_name='Create transfer',
                              entity=self.entity)


class Monitoring(object):

    def __init__(self, cdb):
        self.host = monitoring_host
        self.headers = monitoring_headers
        self.entity = 'monitoring'
        self.tenders_host = tender_host_selector(cdb)[0]
        self.cdb = cdb

    def publish_monitoring(self, json_monitoring):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              method='POST',
                              json_request=json_monitoring,
                              request_name='Publish monitoring',
                              entity=self.entity)

    def patch_monitoring(self, monitoring_id, json_body, message):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              endpoint='/{}'.format(monitoring_id),
                              method='PATCH',
                              json_request=json_body,
                              request_name=message,
                              entity=self.entity)

    def add_post(self, monitoring_id, post_json):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              endpoint='/{}/posts'.format(monitoring_id),
                              method='POST',
                              json_request=post_json,
                              request_name='Add post to monitoring',
                              entity=self.entity)

    def add_document_to_monitoring_entity(self, monitoring_id, entity, json_with_document, message):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              endpoint='/{}/{}'.format(monitoring_id, entity),
                              method='PATCH',
                              json_request=json_with_document,
                              request_name=message,
                              entity=entity)

    def get_monitoring_token(self, monitoring_id, tender_token):
        return request_to_cdb(headers=tender_headers_request(None),
                              host=self.host,
                              endpoint='/{}/credentials?acc_token={}'.format(monitoring_id, tender_token),
                              method='PATCH',
                              json_request=None,
                              request_name='Get monitoring token',
                              entity=self.entity)

    def add_elimination_report(self, monitoring_id, monitoring_token, json_with_report):
        return request_to_cdb(headers=tender_headers_request(json_with_report),
                              host=self.host,
                              endpoint='/{}/eliminationReport?acc_token={}'.format(monitoring_id, monitoring_token),
                              method='PUT',
                              json_request=json_with_report,
                              request_name='Add eliminationReport by tender owner',
                              entity=self.entity)

    def get_monitoring_info(self, monitoring_id):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              endpoint='/{}'.format(monitoring_id),
                              method='GET',
                              json_request=None,
                              request_name='Get monitoring info',
                              entity=self.entity)

    def get_list_of_monitorings(self):
        return request_to_cdb(headers=self.headers,
                              host=self.host,
                              method='GET',
                              json_request=None,
                              request_name='Get list of monitorings',
                              entity=self.entity)
