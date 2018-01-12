# -*- coding: utf-8 -*-
import json
import pytz
import requests
import variables
from variables import tender_values, tender_features, auth_key, lot_values, tender_data, tender_titles, Tenders,\
    tender_values_esco, lot_values_esco
from datetime import datetime, timedelta


# generate list of id fot lots
def list_of_id_for_lots(number_of_lots):
    list_of_lot_id = []
    for x in range(number_of_lots):
        list_of_lot_id.append(variables.lot_id_generator())
    return list_of_lot_id


# generate list of lots
def list_of_lots(number_of_lots, list_of_id_lots):
    list_of_lots_for_tender = []
    for i in range(number_of_lots):
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format(
            '{"id": "', lot_id, '"', variables.title_for_lot(), lot_values[0], '}'))
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}".format(', "lots":', list_of_lots_for_tender)
    return lots_list


def list_of_lots_esco(number_of_lots, list_of_id_lots):
    list_of_lots_for_tender = []
    for i in range(number_of_lots):
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format(
            '{"id": "', lot_id, '"', variables.title_for_lot(), lot_values_esco, '}'))
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}".format(', "lots":', list_of_lots_for_tender)
    return lots_list


# generate items for tender with lots (for lots)
def list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method):
    list_of_items = []
    for i in range(number_of_lots):
        related_lot_id = list_of_id_lots[i]
        item = json.loads(u"{}{}{}{}{}".format(
            '{ "relatedLot": "', related_lot_id, '"', variables.item_data(number_of_lots, number_of_items, i,
                                                                          procurement_method), "}"))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate items for tender without lots
def list_of_items_for_tender(number_of_lots, number_of_items, procurement_method):
    list_of_items = []
    for i in range(number_of_items):
        item = json.loads(u"{}{}{}".format(
            '{', variables.item_data(number_of_lots, number_of_items, i, procurement_method), '}'))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate json for tender with lots
def tender_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}{}".format(
        '{"data": {', tender_values(number_of_lots), tender_titles(), list_of_lots(number_of_lots, list_of_id_lots),
        list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method), tender_features,
        tender_data(procurement_method, accelerator), '}}')


# generate json for tender without lots
def tender(number_of_lots, number_of_items, procurement_method, accelerator):
    tender_json = u"{}{}{}{}{}{}{}".format(
        '{"data": {', tender_values(number_of_lots), tender_titles(),
        list_of_items_for_tender(number_of_lots, number_of_items, procurement_method), tender_features,
        tender_data(procurement_method, accelerator),
        '}}')

    return tender_json


# generate json for tender with lots
def tender_esco_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}{}".format('{"data": {', tender_values_esco(number_of_lots), tender_titles(), list_of_lots_esco(number_of_lots, list_of_id_lots),
                                      list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method), tender_features, tender_data(procurement_method, accelerator), '}}')


# generate json for tender esco without lots
def tender_esco(number_of_lots, number_of_items, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}".format(
        '{"data": {', tender_values_esco(number_of_lots), tender_titles(),
        list_of_items_for_tender(number_of_lots, number_of_items, procurement_method), tender_features,
        tender_data(procurement_method, accelerator),
        '}}')


# generate headers for create tender
def headers_tender(json_tender, headers_host):
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_tender))),
               "Content-Type": "application/json",
               "Host": headers_host}
    return headers


# Publish tender
def publish_tender(headers, json_tender, host, api_version):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('POST',
                             "{}/api/{}/tenders".format(host, api_version),
                             data=json.dumps(json_tender),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 201:
            print("Publishing tender: Success")
            print("       status code:  {}".format(resp.status_code))
            publish_tender_response = {"status_code": resp.status_code, "id": resp.json()['data']['id']}
            return resp, publish_tender_response, resp.status_code
        else:
            print("Publishing tender: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            return resp, resp.content, resp.status_code
    except Exception as e:
        print 'CDB Error'
        return e, 1


# Activate tender
def activating_tender(publish_tender_response, headers, host, api_version):
    try:
        activate_tender = json.loads('{ "data": { "status": "active.tendering"}}')
        tender_location = publish_tender_response.headers['Location']
        token = publish_tender_response.json()['access']['token']
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(host, api_version))
        r = requests.Request('PATCH',
                             "{}{}{}".format(tender_location, '?acc_token=', token),
                             data=json.dumps(activate_tender),
                             headers=headers,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Activating tender: Success")
            print("       status code:  {}".format(resp.status_code))
            activate_tender_response = {"status_code": resp.status_code}
            return 0, resp, activate_tender_response, resp.status_code
        else:
            print("Activating tender: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        return 0, resp, resp.content, resp.status_code
    except Exception as e:
        return 1, e


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
        r = requests.Request('PATCH',
                             "{}{}{}".format(tender_location, '?acc_token=', token),
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
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}/credentials?acc_token={}".format(
                                 host, api_version, second_stage_tender_id, tender_token),
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
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}?acc_token={}".format(
                                 host, api_version, second_stage_tender_id, second_stage_token),
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
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}?acc_token={}".format(host, api_version, new_tender_id, new_token),
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
        tender_to_sql = Tenders(None, tender_id_long, tender_id_short, tender_token,
                                procurement_method, None, tender_status, number_of_lots, None, None, None)
        db.session.add(tender_to_sql)
        db.session.commit()  # you need to call commit() method to save your changes to the database
        print "Tender was added to local database"
        return {"status": "success"}, 0
    except Exception as e:
        return e, 1
