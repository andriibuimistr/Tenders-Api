# -*- coding: utf-8 -*-
import json
import requests
import sys
import variables
from variables import tender_values, tender_features, auth_key, lot_values, tender_data, tender_titles


host = variables.host
api_version = variables.api_version


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
    lots_list = u"{}{}{}".format(variables.lots_m, list_of_lots_for_tender, variables.lots_close)
    return lots_list


# generate items for tender with lots (for lots)
def list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots):
    list_of_items = []
    for i in range(number_of_lots):
        related_lot_id = list_of_id_lots[i]
        item = json.loads(u"{}{}{}{}{}{}".format(
            '{ "relatedLot": ', '"', related_lot_id, '"', variables.item_data(number_of_lots, number_of_items, i), "}"))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(variables.items_m, list_of_items)
    return items_list


# generate items for tender without lots
def list_of_items_for_tender(number_of_lots, number_of_items):
    list_of_items = []
    for i in range(number_of_items):
        item = json.loads(u"{}{}{}".format(
            '{', variables.item_data(number_of_lots, number_of_items, i), "}"))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(variables.items_m, list_of_items)
    return items_list


# generate json for tender with lots
def tender_with_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}{}".format(
        '{"data": {', tender_values(number_of_lots), tender_titles(), list_of_lots(number_of_lots, list_of_id_lots),
        list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots), tender_features,
        tender_data(procurement_method, accelerator), '}}')


# generate json for tender without lots
def tender(number_of_lots, number_of_items, procurement_method, accelerator):
    return u"{}{}{}{}{}{}{}".format(
        '{"data": {', tender_values(number_of_lots), tender_titles(),
        list_of_items_for_tender(number_of_lots, number_of_items), tender_features,
        tender_data(procurement_method, accelerator),
        '}}')


# generate headers for create tender
def headers_tender(json_tender):
    headers = {"Authorization": "Basic {}".format(auth_key),
               "Content-Length": "{}".format(len(json.dumps(json_tender))),
               "Content-Type": "application/json",
               "Host": "lb.api-sandbox.openprocurement.org"}
    return headers


# Publish tender
def publish_tender(headers, json_tender):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(host, api_version))
    r = requests.Request('POST',
                         "{}/api/{}/tenders".format(host, api_version),
                         data=json.dumps(json_tender),
                         headers=headers,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 201:
            print("Publishing tender: Success")
            print("       status code:  {}".format(resp.status_code))
            publish_tender_response = {"status code": resp.status_code, "id": resp.json()['data']['id']}
        else:
            print("Publishing tender: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            print("       tender id:         {}".format(resp.headers['Location'].split('/')[-1]))
            publish_tender_response = {"status code": resp.status_code, "description": resp.headers}
        return resp, publish_tender_response
    except:
        sys.exit("CDB error")


# Activate tender
def activating_tender(publish_tender_response, headers):
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
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        if resp.status_code == 200:
            print("Activating tender: Success")
            print("       status code:  {}".format(resp.status_code))
            activate_tender_response = {"status code": resp.status_code}
        else:
            print("Activating tender: Error")
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
            activate_tender_response = {"status code": resp.status_code, "description": resp.headers}
        return resp, activate_tender_response
    except:
        sys.exit("CDB error")


# save tender info to DB
def tender_to_db(tender_id_long, publish_tender_response, tender_token, procurement_method, tender_status,
                 number_of_lots):
    try:
        # Connect to DB
        db = variables.database()
        # db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
        cursor = db.cursor()
        tender_to_sql = \
            "INSERT INTO tenders VALUES(null, '{}', '{}', '{}', '{}', null, '{}', '{}', null, null, null)".format(
                tender_id_long, publish_tender_response.json()['data']['tenderID'], tender_token, procurement_method,
                tender_status, number_of_lots)
        cursor.execute(tender_to_sql)
        db.commit()  # you need to call commit() method to save your changes to the database
        db.close()
        print "Tender was added to local database"
        return {"status": "success"}
    except:
        sys.exit('Couldn\'t connect to database')
