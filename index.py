# -*- coding: utf-8 -*-
from variables import Companies, Platforms, Roles, Tenders, Bids, db, above_threshold_procurement, below_threshold_procurement, limited_procurement, host_selector, tender_status_list,\
    without_pre_qualification_procedures, prequalification_procedures, competitive_procedures, without_pre_qualification_procedures_status, prequalification_procedures_status, \
    competitive_procedures_status, create_tender_required_fields
import tender
# import document
import bid
import json
import qualification
import time, sys
import refresh
from refresh import get_tender_info
from flask import Flask, jsonify, request, abort, make_response, render_template
from flask_httpauth import HTTPBasicAuth
import re
import validators
from datetime import datetime
from flask_cors import CORS, cross_origin

auth = HTTPBasicAuth()
app = Flask(__name__,)
CORS(app)


@auth.get_password
def get_password(username):
    if username == 'tender':
        return '123456'
    return None


# ###################### ERRORS ################################
@app.errorhandler(400)
def custom400(error):
    return make_response(jsonify(
        {'error': '400 Bad Request', 'description': error.description}), 400)


@auth.error_handler  # 401 error
def unauthorized():
    return make_response(jsonify({'error': '401 Unauthorized access', 'description':
                                 'You are not authorized to access this resource'}), 401)


@app.errorhandler(403)
def custom403(error):
    return make_response(jsonify(
        {'error': '403 Forbidden', 'description': error.description}), 403)


@app.errorhandler(404)
def custom404(error):
    return make_response(jsonify(
        {'error': '404 Not Found', 'description': error.description}), 404)


@app.errorhandler(415)
def custom415(error):
    return make_response(jsonify(
        {'error': '415 Unsupported Media Type', 'description': error.description}), 415)


@app.errorhandler(422)
def custom422(error):
    return make_response(jsonify(
        {'error': '422 Unprocessable Entity', 'description': error.description}), 422)


@app.errorhandler(405)
def custom405(error):
    return make_response(jsonify(
        {'error': '405 Method Not Allowed', 'description': error.description}), 405)


@app.errorhandler(500)
def custom500(error):
    return make_response(jsonify(
        {'error': '500 Internal Server Error', 'description': error.description}), 500)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')


# create tender
@app.route('/api/tenders', methods=['POST'])
@cross_origin(resources=r'/api/*')
def create_tender_function():
    if not request.json:
        abort(400)
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    tc_request = request.json['data']
    for field in range(len(create_tender_required_fields)):
        if create_tender_required_fields[field] not in tc_request:
            abort(400, "Field '{}' is required. List of required fields: {}".format(create_tender_required_fields[field], create_tender_required_fields))

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

    if type(number_of_lots) != int:
        abort(400, 'Number of lots must be integer')
    elif 0 > number_of_lots or number_of_lots > 20:
        abort(422, 'Number of lots must be between 0 and 20')

    if type(number_of_items) != int:
        abort(400, 'Number of items must be integer')
    elif 1 > number_of_items or number_of_items > 20:
        abort(422, 'Number of items must be between 1 and 20')

    '''if type(add_documents) != int:
        abort(400, 'Documents must be integer')
    elif 0 > add_documents or add_documents > 1:
        abort(422, 'Documents must be 0 or 1')

    if type(documents_of_bid) != int:
        abort(400, 'Documents of bid must be integer')
    elif 0 > documents_of_bid or documents_of_bid > 1:
        abort(422, 'Documents of bid must be 0 or 1')'''

    response_json = {}

    if type(number_of_bids) != int:
        abort(400, 'Number of bids must be integer')
    elif 0 > number_of_bids or number_of_bids > 10:
        abort(422, 'Number of bids must be between 0 and 10')

    if type(accelerator) != int:
        abort(400, 'Accelerator must be integer')
    elif 1 > accelerator or accelerator > 30000:
        abort(422, 'Accelerator must be between 1 and 30000')

    if type(company_id) != int:
        abort(400, 'Company ID must be integer')

    if received_tender_status not in tender_status_list:
        return abort(400, 'Tender status must be one of: {}'.format(tender_status_list))

    host_kit = host_selector(api_version)

    # check procurement method
    if procurement_method in above_threshold_procurement:
        # check status for procedure
        if procurement_method in without_pre_qualification_procedures:
            if received_tender_status not in without_pre_qualification_procedures_status:
                return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status))
        elif procurement_method in prequalification_procedures:
            if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status:
                return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status))
        elif procurement_method in competitive_procedures:
            if procurement_method == 'competitiveDialogueUA':
                if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status:
                    return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status +
                                                                                  competitive_procedures_status))

        list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)  # get list of id for lots
        # select type of tender (with or without lots)
        if number_of_lots == 0:
            if procurement_method == 'esco':
                json_tender = json.loads(tender.tender_esco(number_of_lots, number_of_items, procurement_method,
                                                            accelerator))
            else:
                json_tender = json.loads(tender.tender(number_of_lots, number_of_items, procurement_method, accelerator))
        else:
            if procurement_method == 'esco':
                json_tender = json.loads(tender.tender_esco_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                                      procurement_method, accelerator))
            else:
                json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                                 procurement_method, accelerator))
        headers_tender = tender.headers_tender(json_tender, host_kit[3])  # get headers for tender

        # run publish tender function
        publish_tender_response = tender.publish_tender(headers_tender, json_tender, host_kit[0], host_kit[1])  # publish tender in draft status
        if publish_tender_response[0] == 1:
            abort(500, '{}'.format(publish_tender_response[1]))
        elif publish_tender_response[3] != 201:
            abort(publish_tender_response[3], publish_tender_response[2])

        # run activate tender function
        time.sleep(1)
        activate_tender = tender.activating_tender(publish_tender_response[1], headers_tender, host_kit[0], host_kit[1])  # activate tender
        if activate_tender[0] == 1:
            abort(500, activate_tender[1])
        elif activate_tender[3] != 200:
            abort(activate_tender[3], activate_tender[2])

        tender_id_long = publish_tender_response[1].json()['data']['id']
        tender_id_short = publish_tender_response[1].json()['data']['tenderID']
        tender_token = publish_tender_response[1].json()['access']['token']
        tender_status = activate_tender[1].json()['data']['status']

        # add tender to database
        add_tender_db = tender.tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, tender_status, number_of_lots)
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
        response_code = 0
        response_json['status'] = 'error'

        if received_tender_status == 'active.tendering':
            get_t_info = get_tender_info(host_kit, tender_id_long)
            if get_t_info[0] == 200:
                if get_t_info[1].json()['data']['status'] == 'active.tendering':
                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                    response_json['status'] = 'success'
                    response_code = 201
                else:
                    response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                    response_code = 422
            elif get_t_info[0] == 500:
                response_json['tenderStatus'] = str(get_t_info[1])
                response_code = 500
            else:
                response_json['tenderStatus'] = get_t_info[1].json()
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
                            if get_t_info[1].json()['data']['status'] == 'active.stage2.pending':
                                response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                response_json['status'] = 'success'
                                response_code = 201

                                tender.finish_first_stage(publish_tender_response[1], headers_tender, host_kit[0], host_kit[1])
                                attempt_counter = 0
                                for y in range(50):  # check for "completed" status of first stage
                                    attempt_counter += 1
                                    print '{}{}'.format('Check tender status (complete). Attempt ', attempt_counter)
                                    time.sleep(20)
                                    get_t_info = get_tender_info(host_kit, tender_id_long)
                                    if get_t_info[1].json()['data']['status'] == 'complete':
                                        if received_tender_status == 'complete':
                                            response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                            response_json['status'] = 'success'
                                            response_code = 201
                                            break
                                        get_t_info = get_tender_info(host_kit, tender_id_long)  # json with id of 2nd stage
                                        second_stage_tender_id = get_t_info[1].json()['data']['stage2TenderID']  # get id of 2nd stage from json of 1st stage
                                        print '2nd stage id: ' + second_stage_tender_id
                                        get_2nd_stage_info = tender.get_2nd_stage_info(headers_tender, host_kit[0], host_kit[1], second_stage_tender_id, tender_token)  # get info of 2nd stage (with token)
                                        second_stage_token = get_2nd_stage_info[0].json()['access']['token']  # get token of 2nd stage from json

                                        get_t_info = get_tender_info(host_kit, second_stage_tender_id)
                                        second_stage_tender_id_short = get_t_info[1].json()['data']['tenderID']  # get tender id short of 2nd stage
                                        procurement_method_2nd_stage = get_t_info[1].json()['data']['procurementMethodType']
                                        response_json['id'] = second_stage_tender_id_short  # change tender id to 2nd stage tender id for response

                                        get_extended_period_for_2nd_stage = tender.extend_tender_period(host_kit[0], host_kit[1], accelerator, second_stage_tender_id)
                                        tender.patch_second_stage(headers_tender, get_extended_period_for_2nd_stage, host_kit[0], host_kit[1], second_stage_tender_id, second_stage_token)  # ready json 2nd stage
                                        add_2nd_stage_db = tender.tender_to_db(second_stage_tender_id, second_stage_tender_id_short, second_stage_token, procurement_method_2nd_stage, get_t_info[1].json()['data']['status'],
                                                                               number_of_lots)

                                        activate_2nd_stage_json = {  # json for activate second stage
                                            "data": {
                                                "status": "active.tendering"
                                            }
                                        }
                                        tender.activate_2nd_stage(headers_tender, host_kit[0], host_kit[1], second_stage_tender_id, second_stage_token, activate_2nd_stage_json)  # activate 2nd stage request

                                        time.sleep(1)
                                        if received_tender_status == 'active.tendering.stage2':
                                            get_t_info = get_tender_info(host_kit, second_stage_tender_id)
                                            print get_t_info
                                            response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                            response_json['status'] = 'success'
                                            response_code = 201
                                            break

                                        time.sleep(2)
                                        bid_competitive = bid.make_bid_competitive(make_bid[1], second_stage_tender_id, headers_tender, host_kit, procurement_method)  # make bids 2nd stage

                                        get_2nd_stage_actual_json = get_tender_info(host_kit, second_stage_tender_id)
                                        t_end_date = datetime.strptime(get_2nd_stage_actual_json[1].json()['data']['tenderPeriod']['endDate'], '%Y-%m-%dT%H:%M:%S.%f+02:00')  # get tender period end date
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
                                                if get_t_info[1].json()['data']['status'] == 'active.pre-qualification':
                                                    if received_tender_status == 'active.pre-qualification.stage2':
                                                        response_json['tenderStatus'] = get_t_info[1].json()['data']['status']
                                                        response_json['status'] = 'success'
                                                        response_code = 201
                                                        break
                                                    else:
                                                        qualifications = qualification.list_of_qualifications(second_stage_tender_id, host_kit[0], host_kit[1])  # get list of qualifications for tender
                                                        prequalification_result = qualification.pass_second_pre_qualification(qualifications, second_stage_tender_id, second_stage_token, host_kit[0], host_kit[1])  # approve all bids
                                                        time.sleep(2)
                                                        finish_prequalification = qualification.finish_prequalification(second_stage_tender_id, second_stage_token, host_kit[0], host_kit[1])  # submit prequalification protocol
                                                        db.session.remove()

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
                        if get_t_info[0] == 200:
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
                        elif get_t_info[0] == 500:
                            response_json['tenderStatus'] = str(get_t_info[1])
                            response_code = 500
                        else:
                            response_json['tenderStatus'] = get_t_info[1].json()
                            response_code = 422

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

        return jsonify(response_json), response_code

    elif procurement_method in below_threshold_procurement:  # create below threshold procedure
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    elif procurement_method in limited_procurement:  # create limited procedure
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    else:  # incorrect procurementMethodType
        abort(400, 'procurementMethodType must be one of: {}'.format(above_threshold_procurement))


# run synchronization (SQLA)
@app.route('/api/tenders/synchronization', methods=['PATCH'])
@auth.login_required
def update_list_of_tenders():
    update_tenders = refresh.update_tenders_list()
    db.session.close()
    if update_tenders[0] == 0:
        return jsonify({"status": "success", "updated tenders": update_tenders[1]})
    else:
        return jsonify({"status": "error", "description": str(update_tenders[1])})


# get list of all tenders in local database (SQLA)
@app.route('/api/tenders', methods=['GET'])
def get_list_of_tenders():
    list_of_tenders = refresh.get_tenders_list()
    return jsonify({"data": {"tenders": list_of_tenders}})


# ########################## PREQUALIFICATIONS ###################################
# get list of tenders in prequalification status (SQLA)
@app.route('/api/tenders/prequalification', methods=['GET'])
def get_list_tenders_prequalification_status():
    list_tenders_preq = refresh.get_tenders_prequalification_status()
    db.session.remove()
    return jsonify(list_tenders_preq)


# pass prequalification for indicated tender
@app.route('/api/tenders/prequalification/<tender_id_long>', methods=['PATCH'])
@auth.login_required
def pass_prequalification(tender_id_long):
    check_tender_id = Tenders.query.filter_by(tender_id_long=tender_id_long).first().tender_id_long
    if len(check_tender_id) == 0:
        abort(404, 'Tender wasn\'t found in database')
    tender_token = qualification.get_tender_token(tender_id_long)  # get tender token
    if tender_token[0] == 1:
        abort(500, str(tender_token[1]))
    else:
        qualifications = qualification.list_of_qualifications(tender_id_long)  # get list of qualifications for tender
        prequalification_result = qualification.pass_pre_qualification(
            qualifications, tender_id_long, tender_token[1])  # approve all my bids
        time.sleep(2)
        finish_prequalification = qualification.finish_prequalification(
            tender_id_long, tender_token[1])  # submit prequalification protocol
        db.session.remove()
        return jsonify({'data': {"tenderID": tender_id_long, "prequalifications": prequalification_result,
                                 "submit protocol": finish_prequalification}})


# add all tenders to company (SQLA)
@app.route('/api/tenders/company', methods=['POST'])
@auth.login_required
def all_tenders_to_company():
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    tenders_to_company_request = request.json['data']
    if 'company_uid' not in tenders_to_company_request:  # check if company_id is in json
        abort(400, 'Company UID was not found in request')
    company_uid = tenders_to_company_request['company_uid']
    if type(company_uid) != int:
        abort(400, 'Company UID must be integer')
    get_list_of_company_uid = Companies.query.all()
    list_of_uid = []
    for uid in range(len(get_list_of_company_uid)):
        list_of_uid.append(get_list_of_company_uid[uid].id)
    if company_uid in list_of_uid:
        get_company_id = Companies.query.filter_by(id=company_uid).first()
        company_id = get_company_id.company_id
        platform_id = get_company_id.platform_id
        company_role_id = get_company_id.company_role_id
        if company_role_id != 1:
            abort(422, 'Company role must be Buyer (1)')
        get_platform_url = Platforms.query.filter_by(id=platform_id).first()
        company_platform_host = get_platform_url.platform_url
        add_tenders_to_company = refresh.add_all_tenders_to_company(company_id, company_platform_host, company_uid)
        if add_tenders_to_company == 0:
            response_code = 200
        else:
            response_code = 201
        success_message = '{}{}'.format(add_tenders_to_company, ' tenders were added to company')
        db.session.remove()
        return jsonify({"status": "success", "description": success_message}), response_code
    else:
        error_no_uid = '{}{}{}'.format('Company with UID ', company_uid, ' was not found in database')
        print error_no_uid
        db.session.remove()
        return jsonify({"status": "error", "description": error_no_uid})


# add one tender to company (SQLA)
@app.route('/api/tenders/<tender_id_long>/company', methods=['POST'])
@auth.login_required
def add_tender_to_company(tender_id_long):
    list_of_tenders = Tenders.query.all()
    db.session.remove()
    list_tid = []
    for tid in range(len(list_of_tenders)):
        list_tid.append(list_of_tenders[tid].tender_id_long)
    if tender_id_long not in list_tid:
        abort(404, 'Tender id was not found in database')

    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    tender_to_company_request = request.json['data']
    if 'company_uid' not in tender_to_company_request:  # check if company_id is in json
        abort(400, 'Company UID was not found in request')
    company_uid = tender_to_company_request['company_uid']
    if type(company_uid) != int:
        abort(400, 'Company UID must be integer')

    get_list_of_company_uid = Companies.query.all()
    db.session.remove()
    list_of_uid = []
    for uid in range(len(get_list_of_company_uid)):
        list_of_uid.append(int(get_list_of_company_uid[uid].id))
    if company_uid not in list_of_uid:
        abort(422, 'Company was not found in database')
    get_company_id = Companies.query.filter_by(id=company_uid).first()
    db.session.remove()
    company_id = get_company_id.company_id
    platform_id = get_company_id.platform_id
    company_role_id = get_company_id.company_role_id
    if company_role_id != 1:
        abort(422, 'Company role must be Buyer (1)')
    get_platform_url = Platforms.query.filter_by(id=platform_id).first()
    db.session.remove()
    company_platform_host = get_platform_url.platform_url
    add_tender_company = refresh.add_one_tender_to_company(company_id, company_platform_host, tender_id_long,
                                                           company_uid)
    db.session.remove()
    if add_tender_company[1] == 201:
        return jsonify(add_tender_company[0]), 201
    else:
        return jsonify(add_tender_company[0]), 422


# Add new company to database (SQLA)
@app.route('/api/tenders/companies', methods=['POST'])
@auth.login_required
def create_company():
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    cc_request = request.json['data']
    if 'company_email' not in cc_request or 'company_id' not in cc_request \
            or 'company_role_id' not in cc_request or 'platform_id' not in cc_request or 'company_identifier'\
            not in cc_request:
        abort(400, "Can not find one or more parameters.")
    company_email = cc_request['company_email']
    company_id = cc_request['company_id']
    company_role_id = cc_request['company_role_id']
    platform_id = cc_request['platform_id']
    company_identifier = cc_request['company_identifier']

    if type(company_id) != int:
        abort(400, 'Company ID must be integer')
    if type(company_role_id) != int:
        abort(400, 'Company Role ID must be integer')
    if company_identifier.isdigit():
        if len(company_identifier) not in [8, 10]:
            abort(422, 'Company Identifier must be 8 or 10 characters long')
    else:
        abort(400, 'Company Identifier must be numeric')
    if type(platform_id) != int:
        abort(400, 'Platform ID must be integer')

    # check if role exists in database
    check_company_role_id = Roles.query.all()
    list_roles = []
    for rid in range(len(check_company_role_id)):
        list_roles.append(int(check_company_role_id[rid].id))
    if company_role_id not in list_roles:
        abort(422, 'Role wasn\'t found in database')

    # check if platform id exists in database
    check_platform_id = Platforms.query.all()
    list_platforms_id = []
    for pid in range(len(check_platform_id)):
        list_platforms_id.append(int(check_platform_id[pid].id))
    if platform_id not in list_platforms_id:
        abort(422, 'Platform ID wasn\'t found in database')
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", company_email):
        abort(400, 'Email address is invalid')

    # check company_id platform_id combinations
    get_companies_list = Companies.query.all()
    combinations = []
    for combination in range(len(get_companies_list)):
        combinations.append(
            [int(get_companies_list[combination].company_id), int(get_companies_list[combination].platform_id)])
    if [company_id, platform_id] in combinations:
        abort(422, "Company with this ID was added to this platform before")

    add_company = Companies(None, company_email, company_id, company_role_id, platform_id, company_identifier)
    db.session.add(add_company)
    db.session.commit()
    uid = Companies.query.filter_by(company_id=company_id, platform_id=platform_id).first().id
    db.session.remove()
    return jsonify({'status': 'success', 'id': int('{}'.format(uid))})  # return json


# get list of companies in database (SQLA)
@app.route('/api/tenders/companies', methods=['GET'])
@auth.login_required
def get_list_of_companies():
    list_companies = refresh.get_list_of_companies()
    return jsonify({"data": {"companies": list_companies}})


# ##################################### BIDS #############################################
# show all bids of tender (SQLA)
@app.route('/api/tenders/<tender_id_long>/bids', methods=['GET'])
@auth.login_required
def show_bids_of_tender(tender_id_long):
    list_of_tenders = Tenders.query.all()  # 'SELECT tender_id_long FROM tenders'???
    list_tid = []
    for tid in range(len(list_of_tenders)):
        list_tid.append(list_of_tenders[tid].tender_id_long)
    if tender_id_long not in list_tid:
        abort(404, 'Tender id was not found in database')

    get_bids_of_tender = Bids.query.filter_by(tender_id=tender_id_long).all()
    list_of_tender_bids = []
    for every_bid in range(len(get_bids_of_tender)):
        bid_id = get_bids_of_tender[every_bid].bid_id
        bid_token = get_bids_of_tender[every_bid].bid_token
        user_identifier = get_bids_of_tender[every_bid].user_identifier
        company_uid = get_bids_of_tender[every_bid].company_uid
        added_to_site = get_bids_of_tender[every_bid].added_to_site

        list_of_tender_bids.append({"bid_id": bid_id, "bid_token": bid_token,
                                    "user_identifier": user_identifier, "has company": added_to_site})
        if added_to_site == 1:
            list_of_tender_bids[every_bid]['company uid'] = company_uid
            list_of_tender_bids[every_bid]['has company'] = True
        else:
            list_of_tender_bids[every_bid]['has company'] = False
    db.session.remove()
    return jsonify({"data": list_of_tender_bids})


# add one bid to company (SQLA)
@app.route('/api/tenders/bids/<bid_id>/company', methods=['POST'])
@auth.login_required
def add_bid_to_company(bid_id):
    list_of_bids = Bids.query.all()  # 'SELECT tender_id_long FROM tenders'???
    list_bid = []
    for tid in range(len(list_of_bids)):
        list_bid.append(list_of_bids[tid].bid_id)
    if bid_id not in list_bid:
        abort(404, 'Bid id was not found in database')

    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    bid_to_company_request = request.json['data']
    if 'company_uid' not in bid_to_company_request:  # check if company_id is in json
        abort(400, 'Company UID was not found in request')
    company_uid = bid_to_company_request['company_uid']
    if type(company_uid) != int:
        abort(400, 'Company UID must be integer')

    get_list_of_company_uid = Companies.query.all()  # "SELECT id FROM companies"???
    list_of_uid = []
    for uid in range(len(get_list_of_company_uid)):
        list_of_uid.append(int(get_list_of_company_uid[uid].id))
    if company_uid not in list_of_uid:
        abort(422, 'Company was not found in database')
    get_company_id = Companies.query.filter_by(id=company_uid).first()
    company_id = get_company_id.company_id
    platform_id = get_company_id.platform_id
    company_role_id = get_company_id.company_role_id
    if company_role_id != 2:
        abort(422, 'Company role must be Seller (2)')
    get_platform_url = Platforms.query.filter_by(id=platform_id).first()
    company_platform_host = get_platform_url.platform_url
    add_bid_company = refresh.add_one_bid_to_company(company_id, company_platform_host, bid_id, company_uid)
    db.session.remove()
    if add_bid_company[1] == 201:
        return jsonify(add_bid_company[0]), 201
    else:
        return jsonify(add_bid_company)


# get list of platforms
@app.route('/api/tenders/platforms', methods=['GET'])
@auth.login_required
def get_list_of_platforms():
    list_platforms = refresh.get_list_of_platforms()
    return jsonify({"data": {"platforms": list_platforms}})


# create new platform
@app.route('/api/tenders/platforms', methods=['POST'])
@auth.login_required
def add_new_platform():
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    cp_request = request.json['data']
    if 'platform_name' not in cp_request or 'platform_url' not in cp_request:
        abort(400, "Can not find one or more parameters.")
    platform_name = cp_request['platform_name']
    platform_url = cp_request['platform_url']
    if platform_url[-1:] == '/':
        platform_url = platform_url[:-1]

    platforms_url_list = Platforms.query.all()
    list_platform_url = []
    for url in range(len(platforms_url_list)):
        list_platform_url.append(platforms_url_list[url].platform_url)
    if platform_url in list_platform_url:
        abort(422, 'URL exists in database')
    if validators.url(platform_url) is not True:
        abort(400, 'URL is invalid')
    new_platform = Platforms(id=None, platform_name=platform_name, platform_url=platform_url)
    db.session.add(new_platform)
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "success"}), 201


# change existing platform
@app.route('/api/tenders/platforms/<platform_id>', methods=['PATCH'])
@auth.login_required
def patch_platform(platform_id):
    list_pid = []
    list_of_platform_id = Platforms.query.all()
    if platform_id.isdigit() is False:
        abort(400, 'Platform_id must be number')
    for pid in range(len(list_of_platform_id)):
        list_pid.append(list_of_platform_id[pid].id)
    if int(platform_id) not in list_pid:
        abort(404, 'Platform id wasn\'t found in database')
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    cp_request = request.json['data']
    if 'platform_name' not in cp_request and 'platform_url' not in cp_request:
        return jsonify({'data': {
                            "status code": 202,
                            "description": "Nothing was changed"
                        }
                        }), 202
    platform_data = {}
    if 'platform_name' in cp_request:
        platform_data['platform_name'] = cp_request['platform_name']
    if 'platform_url' in cp_request:
        platform_url = cp_request['platform_url']
        if validators.url(platform_url) is not True:
            abort(400, 'URL is invalid')
        else:
            if platform_url[-1:] == '/':
                platform_url = platform_url[:-1]
            platforms_url_list = Platforms.query.all()
            list_platform_url = []
            for url in range(len(platforms_url_list)):
                list_platform_url.append(platforms_url_list[url].platform_url)
            actual_platform_url = Platforms.query.filter_by(id=platform_id).first().platform_url
            print platform_url
            print actual_platform_url
            if platform_url in list_platform_url and platform_url != actual_platform_url:
                abort(422, 'URL exists in database')
            platform_data['platform_url'] = platform_url
    Platforms.query.filter_by(id=platform_id).update(platform_data)
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
