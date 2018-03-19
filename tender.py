# -*- coding: utf-8 -*-
import json
import pytz
import data_for_tender
import qualification
from qualification import run_activate_award, run_activate_contract
from bid import suppliers_for_limited
import refresh
from refresh import check_if_contract_exists, time_counter, count_waiting_time
from data_for_tender import tender_values, features, lot_values, tender_data, tender_titles, tender_values_esco, lot_values_esco, above_threshold_procurement,\
    below_threshold_procurement, limited_procurement, prequalification_procedures, competitive_procedures, negotiation_procurement
from database import db, Tenders
from datetime import datetime, timedelta
import time
from flask import abort
import bid
from tenders.tender_requests import TenderRequests
from TEST2 import generate_tender_json, generate_id_for_lot


# generate list of id fot lots
def list_of_id_for_lots(number_of_lots):
    list_of_lot_id = []
    for x in range(number_of_lots):
        list_of_lot_id.append(data_for_tender.lot_id_generator())
    return list_of_lot_id


# generate list of lots
def list_of_lots(number_of_lots, list_of_id_lots, procurement_method):
    list_of_lots_for_tender = []
    lot_number = 0
    for i in range(number_of_lots):
        lot_number += 1
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format('{"id": "', lot_id, '"', data_for_tender.title_for_lot(lot_number), lot_values[0], '}'))
        if procurement_method in limited_procurement:
            del one_lot['minimalStep'], one_lot['guarantee']
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}".format(', "lots":', list_of_lots_for_tender)
    return lots_list


# generate list of lots for esco procedure
def list_of_lots_esco(number_of_lots, list_of_id_lots):
    list_of_lots_for_tender = []
    lot_number = 0
    for i in range(number_of_lots):
        lot_number += 1
        lot_id = list_of_id_lots[i]
        one_lot = json.loads(u"{}{}{}{}{}{}".format('{"id": "', lot_id, '"', data_for_tender.title_for_lot(lot_number), lot_values_esco, '}'))
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
            item = json.loads(u"{}{}{}{}{}".format('{ "relatedLot": "', related_lot_id, '"', data_for_tender.item_data(number_of_lots, number_of_items, i, procurement_method, item_number), "}"))
            list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate items for tender without lots
def list_of_items_for_tender(number_of_lots, number_of_items, procurement_method):
    list_of_items = []
    item_number = 0
    for i in range(number_of_items):
        item = json.loads(u"{}{}{}".format('{', data_for_tender.item_data(number_of_lots, number_of_items, i, procurement_method, item_number), '}'))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(', "items": ', list_of_items)
    return items_list


# generate json for tender
def json_for_tender(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator, received_tender_status):
    if number_of_lots == 0:
        if procurement_method == 'esco':
            tender_json = u"{}{}{}{}{}{}{}".format('{"data": {', tender_values_esco(number_of_lots), tender_titles(), list_of_items_for_tender(number_of_lots, number_of_items, procurement_method),
                                                   features(procurement_method), tender_data(procurement_method, accelerator, received_tender_status), '}}')
        else:
            tender_json = u"{}{}{}{}{}{}{}".format('{"data": {', tender_values(number_of_lots, procurement_method), tender_titles(), list_of_items_for_tender(number_of_lots, number_of_items, procurement_method),
                                                   features(procurement_method), tender_data(procurement_method, accelerator, received_tender_status), '}}')
    else:
        if procurement_method == 'esco':
            tender_json = u"{}{}{}{}{}{}{}{}".format('{"data": {', tender_values_esco(number_of_lots), tender_titles(), list_of_lots_esco(number_of_lots, list_of_id_lots), list_of_items_for_lots(
                number_of_lots, number_of_items, list_of_id_lots, procurement_method), features(procurement_method), tender_data(procurement_method, accelerator, received_tender_status), '}}')
        else:
            tender_json = u"{}{}{}{}{}{}{}{}".format('{"data": {', tender_values(number_of_lots, procurement_method), tender_titles(), list_of_lots(number_of_lots, list_of_id_lots, procurement_method),
                                                     list_of_items_for_lots(number_of_lots, number_of_items, list_of_id_lots, procurement_method), features(procurement_method), tender_data(
                    procurement_method, accelerator, received_tender_status), '}}')
    return tender_json


# ????????????????????????????????????????????????????? Get tender info
def extend_tender_period(api_version, accelerator, second_stage_tender_id):
    tender_draft = TenderRequests(api_version).get_tender_info(second_stage_tender_id)
    new_tender_json = tender_draft.json()
    kiev_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]
    new_tender_json['data']['tenderPeriod']['endDate'] = str(
        datetime.now() + timedelta(minutes=int(round(11 * (1440.0 / accelerator)) + 1))) + kiev_now
    return new_tender_json


# save tender info to DB (SQLA)
def tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, tender_status, number_of_lots, creator_id, api_version):
    try:
        # Connect to DB
        tender_to_sql = Tenders(None, tender_id_long, tender_id_short, tender_token, procurement_method, None, tender_status, number_of_lots, None, None, None, creator_id, api_version)
        db.session.add(tender_to_sql)
        db.session.commit()
        print "Tender was added to local database"
        return {"status": "success"}, 0
    except Exception as e:
        return e, 1


def creation_of_tender(tc_request, user_id):
    procurement_method = tc_request["procurementMethodType"]
    number_of_lots = int(tc_request["number_of_lots"])
    number_of_items = int(tc_request["number_of_items"])
    number_of_bids = int(tc_request["number_of_bids"])
    accelerator = int(tc_request["accelerator"])
    company_id = int(tc_request['company_id'])
    platform_host = tc_request['platform_host']
    api_version = tc_request['api_version']
    received_tender_status = tc_request['tenderStatus']

    if procurement_method == 'reporting':
        number_of_lots = 0

    response_json = dict()

    list_of_id_lots = generate_id_for_lot(number_of_lots)  # get list of id for lots

    json_tender = json.loads(json_for_tender(number_of_lots, number_of_items, list_of_id_lots, procurement_method, accelerator, received_tender_status))  # get json for create tender
    # json_tender = generate_tender_json(procurement_method, number_of_lots, number_of_items, accelerator, received_tender_status, list_of_id_lots)

    tender = TenderRequests(api_version)
    t_publish = tender.publish_tender(json_tender)

    tender_id_long = t_publish.json()['data']['id']
    tender_token = t_publish.json()['access']['token']
    tender_id_short = t_publish.json()['data']['tenderID']

    time.sleep(1)
    t_activate = tender.activate_tender(tender_id_long, tender_token, procurement_method)
    tender_status = t_activate.json()['data']['status']

    # add tender to database
    add_tender_db = tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, tender_status, number_of_lots, user_id, api_version)
    if add_tender_db[1] == 1:
        abort(500, '{}'.format(add_tender_db[0]))

    add_tender_company = refresh.add_one_tender_company(company_id, platform_host, tender_id_long, 'tender')  # add first stage to company
    response_json['tender_to_company'] = add_tender_company[0], '{}{}{}'.format(platform_host, '/buyer/tender/view/', tender_id_short)

    ''''# add documents to tender
    if add_documents == 1:
        add_documents = document.add_documents_to_tender_ds(tender_id_long, tender_token, list_of_id_lots)
    else:
        add_documents = 'tender was created without documents'''

    print 'Tender id ' + tender_id_long
    print 'Tender token ' + tender_token
    response_json['id'] = tender_id_short
    response_code = 201
    response_json['status'] = 'error'

    if procurement_method in above_threshold_procurement:
        time.sleep(2)
        make_bid = bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method, list_of_id_lots, api_version, 0, json_tender)  # 0 - documents of bid

        if received_tender_status == 'active.tendering':
            get_t_info = tender.get_tender_info(tender_id_long)

            if get_t_info.json()['data']['status'] == 'active.tendering':
                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                response_json['status'] = 'success'
                response_code = 201
            else:
                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                response_code = 422

        else:
            if procurement_method in competitive_procedures:  # qualification for competitive dialogue
                t_end_date = t_publish.json()['data']['tenderPeriod']['endDate']
                waiting_time = count_waiting_time(t_end_date, '%Y-%m-%dT%H:%M:%S+02:00', api_version)
                time_counter(waiting_time, 'Check tender status (pre-qualification)')

                attempt_counter = 0
                for x in range(20):  # check "active.pre-qualification" status
                    attempt_counter += 1
                    print '{}{}'.format('Check tender status (pre-qualification). Attempt ', attempt_counter)
                    time.sleep(30)
                    get_t_info = tender.get_tender_info(tender_id_long)

                    if get_t_info.json()['data']['status'] == 'active.pre-qualification':
                        if received_tender_status == 'active.pre-qualification':
                            response_json['tenderStatus'] = get_t_info.json()['data']['status']
                            response_json['status'] = 'success'
                            response_code = 201
                            break
                        qualifications = qualification.list_of_qualifications(tender_id_long, api_version)  # get list of qualifications for tender
                        qualification.pass_pre_qualification(qualifications, tender_id_long, tender_token, api_version)  # approve all my bids

                        time.sleep(2)
                        tender.finish_prequalification(tender_id_long, tender_token)
                        db.session.remove()
                        waiting_time = int(round(7200.0 / accelerator * 60))
                        time_counter(waiting_time, 'Check tender status (active.stage2.pending)')

                        attempt_counter = 0
                        for y in range(50):  # check for "active.stage2.pending" status
                            attempt_counter += 1
                            print '{}{}'.format('Check tender status (active.stage2.pending). Attempt ',
                                                attempt_counter)
                            time.sleep(20)
                            get_t_info = tender.get_tender_info(tender_id_long)

                            if get_t_info.json()['data']['status'] == 'active.stage2.pending':
                                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201

                                tender.finish_first_stage(tender_id_long, tender_token)  # Finish first stage

                                attempt_counter = 0
                                for z in range(50):  # check for "completed" status of first stage
                                    attempt_counter += 1
                                    print '{}{}'.format('Check tender status (complete). Attempt ', attempt_counter)
                                    time.sleep(20)
                                    get_t_info = tender.get_tender_info(tender_id_long)

                                    if get_t_info.json()['data']['status'] == 'complete':
                                        if received_tender_status == 'complete':
                                            response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                            response_json['status'] = 'success'
                                            response_code = 201
                                            break

                                        second_stage_tender_id = get_t_info.json()['data']['stage2TenderID']  # get id of 2nd stage from json of 1st stage
                                        print '2nd stage id: ' + second_stage_tender_id
                                        get_info_2nd_stage = tender.get_2nd_stage_info(second_stage_tender_id, tender_token)
                                        second_stage_token = get_info_2nd_stage.json()['access']['token']  # get token of 2nd stage from json

                                        get_t_info = tender.get_tender_info(second_stage_tender_id)

                                        second_stage_tender_id_short = get_t_info.json()['data']['tenderID']  # get tender id short of 2nd stage
                                        procurement_method_2nd_stage = get_t_info.json()['data']['procurementMethodType']
                                        response_json['id'] = second_stage_tender_id_short  # change tender id to 2nd stage tender id for response

                                        get_extended_period_for_2nd_stage = extend_tender_period(api_version, accelerator, second_stage_tender_id)
                                        tender.patch_second_stage(second_stage_tender_id, second_stage_token, get_extended_period_for_2nd_stage)
                                        tender_to_db(second_stage_tender_id, second_stage_tender_id_short, second_stage_token, procurement_method_2nd_stage,  # 2nd stage to db
                                                     get_t_info.json()['data']['status'], number_of_lots, user_id, api_version)

                                        tender.activate_2nd_stage(second_stage_tender_id, second_stage_token, procurement_method)

                                        time.sleep(1)
                                        if received_tender_status == 'active.tendering.stage2':
                                            get_t_info = tender.get_tender_info(second_stage_tender_id)

                                            response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                            response_json['status'] = 'success'
                                            response_code = 201
                                            break

                                        time.sleep(2)
                                        bid.make_bid_competitive(make_bid[1], second_stage_tender_id, api_version, procurement_method)  # make bids 2nd stage

                                        get_t_info = tender.get_tender_info(second_stage_tender_id)

                                        t_end_date = get_t_info.json()['data']['tenderPeriod']['endDate']  # get tender period end date
                                        waiting_time = count_waiting_time(t_end_date, '%Y-%m-%dT%H:%M:%S.%f+02:00', api_version)
                                        time_counter(waiting_time, 'Check tender status')

                                        # pass pre-qualification for competitiveDialogueEU
                                        if procurement_method == 'competitiveDialogueEU':
                                            attempt_counter = 0
                                            for v in range(20):
                                                attempt_counter += 1
                                                print '{}{}'.format('Check tender status (pre-qualification 2nd stage). Attempt ', attempt_counter)
                                                time.sleep(30)
                                                get_t_info = tender.get_tender_info(second_stage_tender_id)

                                                if get_t_info.json()['data']['status'] == 'active.pre-qualification':
                                                    if received_tender_status == 'active.pre-qualification.stage2':
                                                        response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                                        response_json['status'] = 'success'
                                                        response_code = 201
                                                        break
                                                    else:
                                                        qualifications = qualification.list_of_qualifications(second_stage_tender_id, api_version)  # get list of qualifications for tender
                                                        qualification.pass_second_pre_qualification(qualifications, second_stage_tender_id, second_stage_token, api_version)  # approve all bids
                                                        time.sleep(2)

                                                        tender.finish_prequalification(second_stage_tender_id, second_stage_token)
                                                        db.session.remove()

                                                        response_code = 200  # change

                                                        waiting_time = int(round(7200.0 / accelerator * 60))
                                                        time_counter(waiting_time, 'Check qualification status')
                                                        break
                                                else:
                                                    if attempt_counter < 20:
                                                        continue
                                                    else:
                                                        abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))

                                        if response_code in [200, 201]:
                                            if received_tender_status == 'active.qualification':
                                                attempt_counter = 0
                                                for attempt in range(30):  # check if 2nd stage is in qualification status
                                                    attempt_counter += 1
                                                    print '{}{}'.format('Check tender status (active.qualification). Attempt ', attempt_counter)
                                                    time.sleep(60)
                                                    get_t_info = tender.get_tender_info(second_stage_tender_id)
                                                    print get_t_info.json()['data']['status']
                                                    if get_t_info.json()['data']['status'] == 'active.qualification':
                                                        response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                                        response_json['status'] = 'success'
                                                        response_code = 201
                                                        break
                                                    else:
                                                        if attempt_counter < 30:

                                                            continue
                                                        else:
                                                            abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))

                                        add_2nd_stage_to_company = refresh.add_one_tender_company(company_id, platform_host, second_stage_tender_id, 'tender')
                                        response_json['second_stage_to_company'] = add_2nd_stage_to_company[0]
                                        response_json['tender_to_company'] = add_2nd_stage_to_company[0], '{}{}{}'.format(platform_host, '/buyer/tender/view/', second_stage_tender_id_short)
                                        break
                                    else:
                                        if attempt_counter < 50:

                                            continue
                                        else:
                                            abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))
                                break
                            else:
                                if attempt_counter < 50:

                                    continue
                                else:
                                    abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))
                        break
                    else:
                        if attempt_counter < 20:

                            continue
                        else:
                            abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))
            else:
                t_end_date = t_publish.json()['data']['tenderPeriod']['endDate']  # get tender period end date
                waiting_time = count_waiting_time(t_end_date, '%Y-%m-%dT%H:%M:%S+02:00', api_version)
                time_counter(waiting_time, 'Check tender status')

                # pass pre-qualification for procedure
                if procurement_method in prequalification_procedures:
                    attempt_counter = 0
                    for x in range(20):
                        attempt_counter += 1
                        print '{}{}'.format('Check tender status (pre-qualification). Attempt ', attempt_counter)
                        time.sleep(30)
                        get_t_info = tender.get_tender_info(tender_id_long)

                        if get_t_info.json()['data']['status'] == 'active.pre-qualification':
                            if received_tender_status == 'active.pre-qualification':
                                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201
                                break
                            else:
                                qualifications = qualification.list_of_qualifications(tender_id_long, api_version)  # get list of qualifications for tender
                                qualification.pass_pre_qualification(qualifications, tender_id_long, tender_token, api_version)  # approve all bids
                                time.sleep(2)
                                tender.finish_prequalification(tender_id_long, tender_token)
                                db.session.remove()

                                response_code = 200  # change

                                waiting_time = int(round(7200.0 / accelerator * 60))
                                time_counter(waiting_time, 'Check qualification status')
                                break
                        else:
                            if attempt_counter < 20:
                                continue
                            else:
                                abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))

                if response_code in [200, 201]:
                    if received_tender_status == 'active.qualification':
                        attempt_counter = 0
                        for attempt in range(30):  # check if tender is in qualification status
                            attempt_counter += 1
                            print '{}{}'.format('Check tender status (active.qualification). Attempt ', attempt_counter)
                            time.sleep(60)
                            get_t_info = tender.get_tender_info(tender_id_long)

                            if get_t_info.json()['data']['status'] == 'active.qualification':
                                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201
                                break
                            else:
                                if attempt_counter < 30:

                                    continue
                                else:
                                    abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))

    elif procurement_method in below_threshold_procurement:
        if received_tender_status == 'active.enquiries':
            get_t_info = tender.get_tender_info(tender_id_long)

            if get_t_info.json()['data']['status'] == 'active.enquiries':
                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                response_json['status'] = 'success'
                response_code = 201
            else:
                abort(422, 'Invalid tender status: {}'.format(get_t_info.json()['data']['status']))

        else:
            get_t_info = tender.get_tender_info(tender_id_long)
            enquiry_end_date = get_t_info.json()['data']['enquiryPeriod']['endDate']  # get tender enquiries end date
            waiting_time = count_waiting_time(enquiry_end_date, '%Y-%m-%dT%H:%M:%S+02:00', api_version)
            if waiting_time > 3600:  # delete in the future
                abort(422, "Waiting time is too long: {} seconds".format(waiting_time))
            time_counter(waiting_time, 'Check tender status (active.tendering)')

            attempt_counter = 0
            for x in range(30):
                attempt_counter += 1
                print '{}{}'.format('Check tender status (active.tendering). Attempt ', attempt_counter)
                time.sleep(20)
                get_t_info = tender.get_tender_info(tender_id_long)

                if get_t_info.json()['data']['status'] == 'active.tendering':
                    bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method, list_of_id_lots, api_version, 0)  # 0 - documents of bid
                    if received_tender_status == 'active.tendering':
                        response_json['tenderStatus'] = get_t_info.json()['data']['status']
                        response_json['status'] = 'success'
                        response_code = 201
                        break
                    t_end_date = t_publish.json()['data']['tenderPeriod']['endDate']  # get tender period end date
                    waiting_time = count_waiting_time(t_end_date, '%Y-%m-%dT%H:%M:%S+02:00', api_version)
                    if waiting_time > 3600:
                        abort(422, "Waiting time is too long: {} seconds".format(waiting_time))
                    time_counter(waiting_time, 'Check tender status')

                    attempt_counter = 0
                    for w in range(60):
                        attempt_counter += 1
                        print '{}{}'.format('Check tender status (active.qualification). Attempt ', attempt_counter)
                        time.sleep(20)
                        get_t_info = tender.get_tender_info(tender_id_long)

                        if get_t_info.json()['data']['status'] == 'active.qualification':
                            if received_tender_status == 'active.qualification':
                                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201
                                break
                    break
    elif procurement_method in limited_procurement:
        if received_tender_status == 'active':
            response_json['tenderStatus'] = 'active'
            response_json['status'] = 'success'
            response_code = 201
        else:
            suppliers_for_limited(number_of_lots, tender_id_long, tender_token, list_of_id_lots, api_version)
            time.sleep(3)

            get_t_info = tender.get_tender_info(tender_id_long)
            list_of_awards = get_t_info.json()['data']['awards']
            if received_tender_status == 'active.award':
                if len(list_of_awards) > 0:
                    response_json['tenderStatus'] = 'active.award'
                    response_json['status'] = 'success'
                    response_code = 201
            else:
                run_activate_award(api_version, tender_id_long, tender_token, list_of_awards, procurement_method)
                time.sleep(3)
                get_t_info = tender.get_tender_info(tender_id_long)
                if procurement_method in negotiation_procurement:
                    complaint_end_date = get_t_info.json()['data']['awards'][-1]['complaintPeriod']['endDate']  # get tender period end date
                    waiting_time = count_waiting_time(complaint_end_date, '%Y-%m-%dT%H:%M:%S.%f+02:00', api_version) + 5
                    if waiting_time > 3600:  # delete in the future
                        abort(400, "Waiting time is too long: {} seconds".format(waiting_time))
                    time_counter(waiting_time, 'Check presence of contract')
                else:
                    complaint_end_date = datetime.now()
                    time.sleep(5)

                for x in range(10):
                    print 'Check if contract exists'
                    get_t_info = tender.get_tender_info(tender_id_long)
                    check_if_contract_exist = check_if_contract_exists(get_t_info)
                    if check_if_contract_exist == 200:
                        if received_tender_status == 'active.contract':
                            response_json['tenderStatus'] = 'active.contract'
                            response_json['status'] = 'success'
                            response_code = 201
                            break
                        else:
                            list_of_contracts = get_t_info.json()['data']['contracts']
                            run_activate_contract(api_version, tender_id_long, tender_token, list_of_contracts, complaint_end_date)
                            for c in range(30):
                                get_t_info = tender.get_tender_info(tender_id_long)
                                if get_t_info.json()['data']['status'] == 'complete':
                                    response_json['tenderStatus'] = get_t_info.json()['data']['status']
                                    response_json['status'] = 'success'
                                    response_code = 201
                                    break
                                else:
                                    print 'Sleep 10 seconds'
                                    time.sleep(10)
                            break
                    else:
                        time.sleep(20)

    return response_json, response_code
