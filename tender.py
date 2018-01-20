# -*- coding: utf-8 -*-
import json
import pytz
import requests
import variables
import qualification
import refresh
from refresh import get_tender_info, get_tender_info2
from variables import db, tender_values, tender_features, auth_key, lot_values, tender_data, tender_titles, Tenders, tender_values_esco, lot_values_esco, above_threshold_procurement,\
    below_threshold_procurement, limited_procurement, host_selector, tender_status_list, without_pre_qualification_procedures, prequalification_procedures, competitive_procedures,\
    without_pre_qualification_procedures_status, prequalification_procedures_status, competitive_procedures_status
from datetime import datetime, timedelta
import time
from flask import abort, jsonify
import bid
import sys


# generate list of id fot lots
def list_of_id_for_lots(number_of_lots):
    list_of_lot_id = []
    for x in range(number_of_lots):
        list_of_lot_id.append(variables.lot_id_generator())
    return list_of_lot_id


# generate list of lots
def list_of_lots(number_of_lots, list_of_id_lots):
    list_of_lots_for_tender = []
    lot_number = 0
    for i in range(number_of_lots):
        lot_number += 1
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format('{"id": "', lot_id, '"', variables.title_for_lot(lot_number), lot_values[0], '}'))
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}".format(', "lots":', list_of_lots_for_tender)
    return lots_list


def list_of_lots_esco(number_of_lots, list_of_id_lots):
    list_of_lots_for_tender = []
    lot_number = 0
    for i in range(number_of_lots):
        lot_number += 1
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format('{"id": "', lot_id, '"', variables.title_for_lot(lot_number), lot_values_esco, '}'))
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}".format(', "lots":', list_of_lots_for_tender)
    return lots_list


# generate items for tender with lots (for lots)
def list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method):
    list_of_items = []
    for i in range(number_of_lots):
        item_number = 0
        related_lot_id = list_of_id_lots[i]
        for item in range(number_of_items):
            item_number += 1
            item = json.loads(u"{}{}{}{}{}".format('{ "relatedLot": "', related_lot_id, '"', variables.item_data(number_of_lots, number_of_items, i, procurement_method, item_number), "}"))
            list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate items for tender without lots
def list_of_items_for_tender(number_of_lots, number_of_items, procurement_method):
    list_of_items = []
    item_number = 0
    for i in range(number_of_items):
        item = json.loads(u"{}{}{}".format('{', variables.item_data(number_of_lots, number_of_items, i, procurement_method, item_number), '}'))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate json for tender with lots
def tender_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}{}".format('{"data": {', tender_values(number_of_lots), tender_titles(), list_of_lots(number_of_lots, list_of_id_lots),
                                      list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method), tender_features, tender_data(procurement_method, accelerator), '}}')


# generate json for tender without lots
def tender(number_of_lots, number_of_items, procurement_method, accelerator):
    tender_json = u"{}{}{}{}{}{}{}".format('{"data": {', tender_values(number_of_lots), tender_titles(), list_of_items_for_tender(number_of_lots, number_of_items, procurement_method), tender_features,
                                           tender_data(procurement_method, accelerator), '}}')
    return tender_json


# generate json for tender with lots
def tender_esco_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}{}".format('{"data": {', tender_values_esco(number_of_lots), tender_titles(), list_of_lots_esco(number_of_lots, list_of_id_lots),
                                      list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method), tender_features, tender_data(procurement_method, accelerator), '}}')


# generate json for tender esco without lots
def tender_esco(number_of_lots, number_of_items, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}".format('{"data": {', tender_values_esco(number_of_lots), tender_titles(), list_of_items_for_tender(number_of_lots, number_of_items, procurement_method), tender_features,
                                    tender_data(procurement_method, accelerator), '}}')


# generate headers for create tender
def headers_request(json_tender, headers_host):
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_tender))),
               "Content-Type": "application/json",
               "Host": headers_host}
    return headers


# Publish tender
def publish_tender(headers, json_tender, host, api_version):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            s = requests.Session()
            s.request("GET", "{}/api/{}/tenders".format(host, api_version))
            r = requests.Request('POST', "{}/api/{}/tenders".format(host, api_version),
                                 data=json.dumps(json_tender),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))

            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 201:
                print("Publishing tender: Success")
                print("       status code:  {}".format(resp.status_code))
                # publish_tender_response = {"status_code": resp.status_code, "id": resp.json()['data']['id']}
                return 0, resp, resp.content, resp.status_code
            else:
                print("Publishing tender: Error")
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                if attempts >= 5:
                    return 0, resp, resp.content, resp.status_code
        except Exception as e:
            print 'CDB Error'
            if attempts < 5:
                continue
            else:
                return 1, 'Publish tender error: ' + str(e)


# Activate tender
def activating_tender(publish_tender_response, headers, host, api_version, procurement_method):
    attempts = 0
    for x in range(5):
        attempts += 1
        try:
            if procurement_method in variables.above_threshold_procurement:
                activate_tender = json.loads('{ "data": { "status": "active.tendering"}}')
            elif procurement_method in variables.below_threshold_procurement:
                activate_tender = json.loads('{ "data": { "status": "active.enquiries"}}')
            else:
                activate_tender = 'LIMITED PROCEDURE ACTIVATING JSON!!!'
            tender_location = publish_tender_response.headers['Location']
            token = publish_tender_response.json()['access']['token']
            s = requests.Session()
            s.request("GET", "{}/api/{}/tenders".format(host, api_version))
            r = requests.Request('PATCH', "{}{}{}".format(tender_location, '?acc_token=', token),
                                 data=json.dumps(activate_tender),
                                 headers=headers,
                                 cookies=requests.utils.dict_from_cookiejar(s.cookies))
            prepped = s.prepare_request(r)
            resp = s.send(prepped)
            if resp.status_code == 200:
                print("Activating tender: Success")
                print("       status code:  {}".format(resp.status_code))
                # activate_tender_response = {"status_code": resp.status_code}
                return 0, resp, resp.content, resp.status_code
            else:
                print("Activating tender: Error")
                print("       status code:  {}".format(resp.status_code))
                print("       response content:  {}".format(resp.content))
                print("       headers:           {}".format(resp.headers))
                if attempts >= 5:
                    return 0, resp, resp.content, resp.status_code
        except Exception as e:
            if attempts < 5:
                continue
            else:
                return 1, 'Activate tender error: ' + str(e)


# Finish first stage
def finish_first_stage(publish_tender_response, headers, host, api_version):
    try:
        finish_stage_one = {
                              "data": {
                                "status": "active.stage2.waiting"
                              }
                            }
        tender_location = publish_tender_response.headers['Location']
        token = publish_tender_response.json()['access']['token']
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH', "{}{}{}".format(tender_location, '?acc_token=', token),
                             data=json.dumps(finish_stage_one),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Finish first stage: Success")
            print("       status code:  {}".format(resp.status_code))
            activate_tender_response = {"status_code": resp.status_code}
            return 0, resp, activate_tender_response, resp.status_code
        else:
            print("Finish first stage: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return 0, resp, resp.content, resp.status_code
    except Exception as e:
        return 1, e


def get_2nd_stage_info(headers, host, api_version, second_stage_tender_id, tender_token):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH', "{}/api/{}/tenders/{}/credentials?acc_token={}".format(host, api_version, second_stage_tender_id, tender_token),
                             data=json.dumps('{}'),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Get 2nd stage json: Success")
            print("       status code:  {}".format(resp.status_code))
            # print("  token 2-nd stage:  {}".format(resp.json()['access']['token']))
            publish_tender_response = {"status_code": resp.status_code, "id": resp.json()['data']['id']}
            return resp, publish_tender_response, resp.status_code
        else:
            print("Get 2nd stage json: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            return resp, resp.content, resp.status_code
    except Exception as e:
        print e
        return e, 1


def extend_tender_period(host, api_version, accelerator, second_stage_tender_id):
    tender_draft = requests.get("{}/api/{}/tenders/{}".format(host, api_version, second_stage_tender_id))
    new_tender_json = tender_draft.json()
    kiev_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]
    new_tender_json['data']['tenderPeriod']['endDate'] = str(
        datetime.now() + timedelta(minutes=int(round(11 * (1440.0 / accelerator)) + 1))) + kiev_now
    return new_tender_json


# Patch second stage
def patch_second_stage(headers, new_tender_json, host, api_version, second_stage_tender_id, second_stage_token):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH', "{}/api/{}/tenders/{}?acc_token={}".format(host, api_version, second_stage_tender_id, second_stage_token),
                             data=json.dumps(new_tender_json),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Patch 2nd stage: Success")
            print("       status code:  {}".format(resp.status_code))
            publish_tender_response = {"status_code": resp.status_code, "id": resp.json()['data']['id']}
            return resp, publish_tender_response, resp.status_code
        else:
            print("Patch 2nd stage: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            return resp, resp.content, resp.status_code
    except Exception as e:
        print 'CDB Error'
        return e, 1


def activate_2nd_stage(headers, host, api_version, new_tender_id, new_token, activate_2nd_stage_json):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH', "{}/api/{}/tenders/{}?acc_token={}".format(host, api_version, new_tender_id, new_token),
                             data=json.dumps(activate_2nd_stage_json),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Activate 2nd stage: Success")
            print("       status code:  {}".format(resp.status_code))
            print("  token 2-nd stage:  {}".format(resp.json()['access']['token']))
            publish_tender_response = {"status_code": resp.status_code, "id": resp.json()['data']['id']}
            return resp, publish_tender_response, resp.status_code
        else:
            print("Activate 2nd stage: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            return resp, resp.content, resp.status_code
    except Exception as e:
        return e, 1


# save tender info to DB (SQLA)
def tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, tender_status,
                 number_of_lots):
    try:
        # Connect to DB
        db = variables.db
        tender_to_sql = Tenders(None, tender_id_long, tender_id_short, tender_token, procurement_method, None, tender_status, number_of_lots, None, None, None)
        db.session.add(tender_to_sql)
        db.session.commit()  # you need to call commit() method to save your changes to the database
        print "Tender was added to local database"
        return {"status": "success"}, 0
    except Exception as e:
        return e, 1


def creation_of_tender(tc_request):
    procurement_method = tc_request["procurementMethodType"]
    number_of_lots = tc_request["number_of_lots"]
    number_of_items = tc_request["number_of_items"]
    # add_documents = tc_request["documents"]
    # documents_of_bid = tc_request["documents_bid"]
    number_of_bids = tc_request["number_of_bids"]
    accelerator = tc_request["accelerator"]
    company_id = tc_request['company_id']
    platform_host = tc_request['platform_host']
    api_version = tc_request['api_version']
    received_tender_status = tc_request['tenderStatus']

    host_kit = host_selector(api_version)
    response_json = dict()

    list_of_id_lots = list_of_id_for_lots(number_of_lots)  # get list of id for lots
    # select type of tender (with or without lots)
    if number_of_lots == 0:
        if procurement_method == 'esco':
            json_tender = json.loads(tender_esco(number_of_lots, number_of_items, procurement_method, accelerator))
        else:
            json_tender = json.loads(tender(number_of_lots, number_of_items, procurement_method, accelerator))
    else:
        if procurement_method == 'esco':
            json_tender = json.loads(tender_esco_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator))
        else:
            json_tender = json.loads(tender_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator))
    headers_tender = headers_request(json_tender, host_kit[3])  # get headers for tender

    # run publish tender function
    publish_tender_response = publish_tender(headers_tender, json_tender, host_kit[0], host_kit[1])  # publish tender in draft status
    if publish_tender_response[0] == 1:
        abort(500, '{}'.format(publish_tender_response[1]))
    elif publish_tender_response[3] != 201:
        if 'application/json' in publish_tender_response[1].headers['Content-Type']:
            error_reason = publish_tender_response[2]
        else:
            error_reason = str(publish_tender_response[2])
        abort(publish_tender_response[3], error_reason)

    # run activate tender function
    time.sleep(1)
    activate_tender = activating_tender(publish_tender_response[1], headers_tender, host_kit[0], host_kit[1], procurement_method)  # activate tender
    if activate_tender[0] == 1:
        abort(500, activate_tender[1])
    elif activate_tender[3] != 200:
        if 'application/json' in activate_tender[1].headers['Content-Type']:
            error_reason = activate_tender[2]
        else:
            error_reason = str(activate_tender[2])
        abort(activate_tender[3], error_reason)

    tender_id_long = publish_tender_response[1].json()['data']['id']
    tender_id_short = publish_tender_response[1].json()['data']['tenderID']
    tender_token = publish_tender_response[1].json()['access']['token']
    tender_status = activate_tender[1].json()['data']['status']

    # add tender to database
    add_tender_db = tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, tender_status, number_of_lots)
    if add_tender_db[1] == 1:
        abort(500, '{}'.format(add_tender_db[0]))

    ''''# add documents to tender
    if add_documents == 1:
        add_documents = document.add_documents_to_tender_ds(tender_id_long, tender_token, list_of_id_lots)
    else:
        add_documents = 'tender was created without documents'''
    time.sleep(2)
    make_bid = bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method, list_of_id_lots, host_kit, 0)  # 0 - documents of bid

    print 'Tender id ' + tender_id_long
    print 'Tender token ' + tender_token
    response_json['id'] = tender_id_short
    response_code = 201
    response_json['status'] = 'error'

    if received_tender_status == 'active.tendering':
        get_t_info = get_tender_info(host_kit, tender_id_long)
        if get_t_info[0] == 500:
            response_json['tenderStatus'] = str(get_t_info[1])
            response_code = 500
        elif get_t_info[0] not in [500, 200]:
            response_json['tenderStatus'] = get_t_info[1].json()
            response_code = 422
        else:
            if get_t_info[1].json()['data']['status'] == 'active.tendering':
                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                response_json['status'] = 'success'
                response_code = 201
            else:
                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                response_code = 422

    else:
        if procurement_method in competitive_procedures:  # qualification for competitive dialogue
            t_end_date = datetime.strptime(publish_tender_response[1].json()['data']['tenderPeriod']['endDate'], '%Y-%m-%dT%H:%M:%S+02:00')
            waiting_time = (t_end_date - datetime.now()).seconds
            for remaining in range(waiting_time, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\rWaiting for pre-qualification status            \n")
            attempt_counter = 0
            for x in range(20):  # check "active.pre-qualification" status
                attempt_counter += 1
                print '{}{}'.format('Check tender status (pre-qualification). Attempt ', attempt_counter)
                time.sleep(30)
                get_t_info = get_tender_info(host_kit, tender_id_long)

                if get_t_info[0] == 500:
                    response_json['tenderStatus'] = str(get_t_info[1])
                    response_code = 500
                    if attempt_counter >= 20:
                        break
                elif get_t_info[0] not in [500, 200]:
                    response_json['tenderStatus'] = get_t_info[1].json()
                    response_code = 422
                    if attempt_counter >= 20:
                        break
                else:
                    if get_t_info[1].json()['data']['status'] == 'active.pre-qualification':
                        if received_tender_status == 'active.pre-qualification':
                            response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                            response_json['status'] = 'success'
                            response_code = 201
                            break
                        qualifications = qualification.list_of_qualifications(tender_id_long, host_kit[0], host_kit[1])  # get list of qualifications for tender
                        prequalification_result = qualification.pass_pre_qualification(qualifications, tender_id_long, tender_token, host_kit[0], host_kit[1])  # approve all my bids
                        time.sleep(2)
                        finish_prequalification = qualification.finish_prequalification(
                            tender_id_long, tender_token, host_kit[0], host_kit[1])  # submit prequalification protocol
                        db.session.remove()
                        waiting_time = int(round(7200.0 / accelerator * 60))
                        for remaining in range(waiting_time, 0, -1):
                            sys.stdout.write("\r")
                            sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                            sys.stdout.flush()
                            time.sleep(1)
                        sys.stdout.write("\rComplete!            \n")
                        attempt_counter = 0
                        for y in range(50):  # check for "active.stage2.pending" status
                            attempt_counter += 1
                            print '{}{}'.format('Check tender status (active.stage2.pending). Attempt ',
                                                attempt_counter)
                            time.sleep(20)
                            get_t_info = get_tender_info(host_kit, tender_id_long)

                            if get_t_info[0] == 500:
                                response_json['tenderStatus'] = str(get_t_info[1])
                                response_code = 500
                                if attempt_counter >= 50:
                                    break
                            elif get_t_info[0] not in [500, 200]:
                                response_json['tenderStatus'] = get_t_info[1].json()
                                response_code = 422
                                if attempt_counter >= 50:
                                    break
                            else:
                                if get_t_info[1].json()['data']['status'] == 'active.stage2.pending':
                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                    response_json['status'] = 'success'
                                    response_code = 201

                                    finish_first_stage(publish_tender_response[1], headers_tender, host_kit[0], host_kit[1])
                                    attempt_counter = 0
                                    for y in range(50):  # check for "completed" status of first stage
                                        attempt_counter += 1
                                        print '{}{}'.format('Check tender status (complete). Attempt ', attempt_counter)
                                        time.sleep(20)
                                        get_t_info = get_tender_info(host_kit, tender_id_long)

                                        if get_t_info[0] == 500:
                                            response_json['tenderStatus'] = str(get_t_info[1])
                                            response_code = 500
                                            if attempt_counter >= 50:
                                                break
                                        elif get_t_info[0] not in [500, 200]:
                                            response_json['tenderStatus'] = get_t_info[1].json()
                                            response_code = 422
                                            if attempt_counter >= 50:
                                                break
                                        else:
                                            if get_t_info[1].json()['data']['status'] == 'complete':
                                                if received_tender_status == 'complete':
                                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                    response_json['status'] = 'success'
                                                    response_code = 201
                                                    break

                                                second_stage_tender_id = get_t_info[1].json()['data']['stage2TenderID']  # get id of 2nd stage from json of 1st stage
                                                print '2nd stage id: ' + second_stage_tender_id
                                                get_info_2nd_stage = get_2nd_stage_info(headers_tender, host_kit[0], host_kit[1], second_stage_tender_id, tender_token)  # get info of 2nd stage (with token)
                                                second_stage_token = get_info_2nd_stage[0].json()['access']['token']  # get token of 2nd stage from json

                                                get_t_info = get_tender_info(host_kit, second_stage_tender_id)
                                                if get_t_info[0] == 500:
                                                    response_json['tenderStatus'] = str(get_t_info[1])
                                                    response_code = 500
                                                    break
                                                elif get_t_info[0] not in [500, 200]:
                                                    response_json['tenderStatus'] = get_t_info[1].json()
                                                    response_code = 422
                                                    break
                                                second_stage_tender_id_short = get_t_info[1].json()['data']['tenderID']  # get tender id short of 2nd stage
                                                procurement_method_2nd_stage = get_t_info[1].json()['data']['procurementMethodType']
                                                response_json['id'] = second_stage_tender_id_short  # change tender id to 2nd stage tender id for response

                                                get_extended_period_for_2nd_stage = extend_tender_period(host_kit[0], host_kit[1], accelerator, second_stage_tender_id)
                                                patch_second_stage(headers_tender, get_extended_period_for_2nd_stage, host_kit[0], host_kit[1], second_stage_tender_id, second_stage_token)  # ready json 2nd stage
                                                add_2nd_stage_db = tender_to_db(second_stage_tender_id, second_stage_tender_id_short, second_stage_token, procurement_method_2nd_stage,
                                                                                       get_t_info[1].json()['data']['status'],
                                                                                       number_of_lots)

                                                activate_2nd_stage_json = {  # json for activate second stage
                                                    "data": {
                                                        "status": "active.tendering"
                                                    }
                                                }
                                                activate_2nd_stage(headers_tender, host_kit[0], host_kit[1], second_stage_tender_id, second_stage_token, activate_2nd_stage_json)  # activate 2nd stage request

                                                time.sleep(1)
                                                if received_tender_status == 'active.tendering.stage2':
                                                    get_t_info = get_tender_info(host_kit, second_stage_tender_id)
                                                    if get_t_info[0] == 500:
                                                        response_json['tenderStatus'] = str(get_t_info[1])
                                                        response_code = 500
                                                        break
                                                    elif get_t_info[0] not in [500, 200]:
                                                        response_json['tenderStatus'] = get_t_info[1].json()
                                                        response_code = 422
                                                        break
                                                    print get_t_info
                                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                    response_json['status'] = 'success'
                                                    response_code = 201
                                                    break

                                                time.sleep(2)
                                                bid_competitive = bid.make_bid_competitive(make_bid[1], second_stage_tender_id, headers_tender, host_kit, procurement_method)  # make bids 2nd stage

                                                get_t_info = get_tender_info(host_kit, second_stage_tender_id)

                                                if get_t_info[0] == 500:
                                                    response_json['tenderStatus'] = str(get_t_info[1])
                                                    response_code = 500
                                                    break
                                                elif get_t_info[0] not in [500, 200]:
                                                    response_json['tenderStatus'] = get_t_info[1].json()
                                                    response_code = 422
                                                    break

                                                t_end_date = datetime.strptime(get_t_info[1].json()['data']['tenderPeriod']['endDate'], '%Y-%m-%dT%H:%M:%S.%f+02:00')  # get tender period end date
                                                waiting_time = (t_end_date - datetime.now()).seconds
                                                for remaining in range(waiting_time, 0, -1):
                                                    sys.stdout.write("\r")
                                                    sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                                                    sys.stdout.flush()
                                                    time.sleep(1)
                                                sys.stdout.write("\rCheck tender status            \n")

                                                # pass pre-qualification for competitiveDialogueEU
                                                if procurement_method == 'competitiveDialogueEU':
                                                    attempt_counter = 0
                                                    for x in range(20):
                                                        attempt_counter += 1
                                                        print '{}{}'.format('Check tender status (pre-qualification 2nd stage). Attempt ', attempt_counter)
                                                        time.sleep(30)
                                                        get_t_info = get_tender_info(host_kit, second_stage_tender_id)

                                                        if get_t_info[0] == 500:
                                                            response_json['tenderStatus'] = str(get_t_info[1])
                                                            response_code = 500
                                                            break
                                                        elif get_t_info[0] not in [500, 200]:
                                                            response_json['tenderStatus'] = get_t_info[1].json()
                                                            response_code = 422
                                                            break

                                                        if get_t_info[1].json()['data']['status'] == 'active.pre-qualification':
                                                            if received_tender_status == 'active.pre-qualification.stage2':
                                                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                                response_json['status'] = 'success'
                                                                response_code = 201
                                                                break
                                                            else:
                                                                qualifications = qualification.list_of_qualifications(second_stage_tender_id, host_kit[0], host_kit[1])  # get list of qualifications for tender
                                                                prequalification_result = qualification.pass_second_pre_qualification(qualifications, second_stage_tender_id, second_stage_token, host_kit[0],
                                                                                                                                      host_kit[1])  # approve all bids
                                                                time.sleep(2)
                                                                finish_prequalification = qualification.finish_prequalification(second_stage_tender_id, second_stage_token, host_kit[0],
                                                                                                                                host_kit[1])  # submit prequalification protocol
                                                                db.session.remove()

                                                                response_code = 200  # change

                                                                waiting_time = int(round(7200.0 / accelerator * 60))
                                                                for remaining in range(waiting_time, 0, -1):
                                                                    sys.stdout.write("\r")
                                                                    sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                                                                    sys.stdout.flush()
                                                                    time.sleep(1)
                                                                sys.stdout.write("\rWaiting for qualification status            \n")
                                                                break
                                                        else:
                                                            if attempt_counter < 20:
                                                                continue
                                                            else:
                                                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                                response_json['status'] = 'error'
                                                                response_code = 422

                                                if response_code in [200, 201]:
                                                    if received_tender_status == 'active.qualification':
                                                        attempt_counter = 0
                                                        for attempt in range(30):  # check if 2nd stage is in qualification status
                                                            attempt_counter += 1
                                                            print '{}{}'.format('Check tender status (active.qualification). Attempt ', attempt_counter)
                                                            time.sleep(60)
                                                            get_t_info = get_tender_info(host_kit, second_stage_tender_id)
                                                            print get_t_info[1].json()['data']['status']
                                                            if get_t_info[1].json()['data']['status'] == 'active.qualification':
                                                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                                response_json['status'] = 'success'
                                                                response_code = 201
                                                                break
                                                            else:
                                                                if attempt_counter < 30:

                                                                    continue
                                                                else:
                                                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                                    response_json['status'] = 'error'
                                                                    response_code = 422

                                                add_2nd_stage_to_company = refresh.add_one_tender_company(company_id, platform_host, second_stage_tender_id)
                                                response_json['second_stage_to_company'] = add_2nd_stage_to_company[0]
                                                break
                                            else:
                                                if attempt_counter < 50:

                                                    continue
                                                else:
                                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                    response_json['status'] = 'error'
                                                    response_code = 422
                                    break
                                else:
                                    if attempt_counter < 50:

                                        continue
                                    else:
                                        response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                        response_json['status'] = 'error'
                                        response_code = 422
                        break
                    else:
                        if attempt_counter < 20:

                            continue
                        else:
                            response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                            response_json['status'] = 'error'
                            response_code = 422
        else:
            t_end_date = datetime.strptime(publish_tender_response[1].json()['data']['tenderPeriod']['endDate'], '%Y-%m-%dT%H:%M:%S+02:00')  # get tender period end date
            waiting_time = (t_end_date - datetime.now()).seconds
            for remaining in range(waiting_time, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\rCheck tender status            \n")

            # pass pre-qualification for procedure
            if procurement_method in prequalification_procedures:
                attempt_counter = 0
                for x in range(20):
                    attempt_counter += 1
                    print '{}{}'.format('Check tender status (pre-qualification). Attempt ', attempt_counter)
                    time.sleep(30)
                    get_t_info = get_tender_info(host_kit, tender_id_long)

                    if get_t_info[0] == 500:
                        response_json['tenderStatus'] = str(get_t_info[1])
                        response_code = 500
                    elif get_t_info[0] not in [500, 200]:
                        response_json['tenderStatus'] = get_t_info[1].json()
                        response_code = 422
                    else:
                        if get_t_info[1].json()['data']['status'] == 'active.pre-qualification':
                            if received_tender_status == 'active.pre-qualification':
                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201
                                break
                            else:
                                qualifications = qualification.list_of_qualifications(tender_id_long, host_kit[0], host_kit[1])  # get list of qualifications for tender
                                prequalification_result = qualification.pass_pre_qualification(qualifications, tender_id_long, tender_token, host_kit[0], host_kit[1])  # approve all bids
                                time.sleep(2)
                                finish_prequalification = qualification.finish_prequalification(tender_id_long, tender_token, host_kit[0], host_kit[1])  # submit prequalification protocol
                                db.session.remove()

                                response_code = 200  # change

                                waiting_time = int(round(7200.0 / accelerator * 60))
                                for remaining in range(waiting_time, 0, -1):
                                    sys.stdout.write("\r")
                                    sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                                    sys.stdout.flush()
                                    time.sleep(1)
                                sys.stdout.write("\rWaiting for qualification status            \n")
                                break
                        else:
                            if attempt_counter < 20:
                                continue
                            else:
                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                response_code = 422

            if response_code in [200, 201]:
                if received_tender_status == 'active.qualification':
                    attempt_counter = 0
                    for attempt in range(30):  # check if 2nd stage is in qualification status
                        attempt_counter += 1
                        print '{}{}'.format('Check tender status (active.qualification). Attempt ', attempt_counter)
                        time.sleep(60)
                        get_t_info = get_tender_info(host_kit, tender_id_long)

                        if get_t_info[0] == 200:
                            if get_t_info[1].json()['data']['status'] == 'active.qualification':
                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201
                                break
                            else:
                                if attempt_counter < 30:

                                    continue
                                else:
                                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                    response_code = 422
                        elif get_t_info[0] == 500:
                            response_json['tenderStatus'] = str(get_t_info[1])
                            response_code = 500
                        else:
                            response_json['tenderStatus'] = get_t_info[1].json()
                            response_code = 422

    add_tender_company = refresh.add_one_tender_company(company_id, platform_host, tender_id_long)  # add first stage to company
    response_json['tender_to_company'] = add_tender_company[0]

    return response_json, response_code
