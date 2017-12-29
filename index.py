# -*- coding: utf-8 -*-
from variables import Companies, Platforms, Roles, Tenders, Bids, db, above_threshold_procurement,\
    below_threshold_procurement, limited_procurement, host_selector, prequalification_procedures,\
    tender_status_list
import tender
# import document
import bid
import json
import qualification
import time
import refresh
from flask import Flask, jsonify, request, abort, make_response, render_template
from flask_httpauth import HTTPBasicAuth
import re
import validators
import requests
from datetime import datetime


auth = HTTPBasicAuth()
app = Flask(__name__,)


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


@app.route('/')
def index():
    return render_template('index.html')


# create tender
@app.route('/api/tenders', methods=['POST'])
def create_tender_function():
    if not request.json:
        abort(400)
    if 'data' not in request.json:  # check if data is in json
        abort(400, 'Data was not found in request')
    tc_request = request.json['data']
    if 'procurementMethodType' not in tc_request or 'number_of_lots' not in tc_request \
            or 'number_of_items' not in tc_request or 'number_of_bids' not in tc_request \
            or 'accelerator' not in tc_request or 'company_id' not in tc_request or 'platform_host' not in tc_request \
            or 'api_version' not in tc_request or not 'tenderStatus' in tc_request:
        abort(400, "One or more parameters are incorrect.")

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
    elif 0 > number_of_lots or number_of_lots > 10:
        abort(422, 'Number of lots must be between 0 and 10')

    if type(number_of_items) != int:
        abort(400, 'Number of items must be integer')
    elif 1 > number_of_items or number_of_items > 10:
        abort(422, 'Number of items must be between 1 and 10')

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
    elif 1 > accelerator or accelerator > 20000:
        abort(422, 'Accelerator must be between 1 and 15000')

    if type(company_id) != int:
        abort(400, 'Company ID must be integer')

    if received_tender_status not in tender_status_list:
        return abort(400, 'Incorrect tender status')
    if received_tender_status == 'active.pre-qualification':
        if procurement_method not in prequalification_procedures:
            abort(422, '{} {}'.format(procurement_method, "has no 'prequalification' status"))


    host_kit = host_selector(api_version)

    # check procurement method
    if procurement_method in above_threshold_procurement:
        list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)  # get list of id for lots
        # select type of tender (with or without lots)
        if number_of_lots == 0:
            if procurement_method == 'esco':
                json_tender = json.loads(tender.tender_esco(number_of_lots, number_of_items, procurement_method,
                                                            accelerator))
            else:
                json_tender = json.loads(tender.tender(
                    number_of_lots, number_of_items, procurement_method, accelerator))
        else:
            if procurement_method == 'esco':
                json_tender = json.loads(tender.tender_esco_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                                      procurement_method, accelerator))
            else:
                json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                                 procurement_method, accelerator))
        headers_tender = tender.headers_tender(json_tender, host_kit[3])  # get headers for tender

        # run publish tender function
        publish_tender_response = tender.publish_tender(
            headers_tender, json_tender, host_kit[0], host_kit[1])  # publish tender in draft status
        if publish_tender_response[1] == 1:
            abort(500, '{}'.format(publish_tender_response[0]))
        elif publish_tender_response[2] != 201:
            abort(publish_tender_response[2], json.loads(publish_tender_response[1]))

        tender_id = publish_tender_response[0].json()['data']['id']

        # run activate tender function
        activate_tender = tender.activating_tender(
            publish_tender_response[0], headers_tender, host_kit[0], host_kit[1])  # activate tender
        if activate_tender[0] == 1:
            abort(500, '{}'.format(activate_tender[0]))
        elif activate_tender[3] != 200:
            abort(activate_tender[3], str(activate_tender[2]))

        tender_id_long = publish_tender_response[0].headers['Location'].split('/')[-1]
        tender_token = publish_tender_response[0].json()['access']['token']
        tender_status = activate_tender[1].json()['data']['status']

        # add tender to database
        add_tender_db = tender.tender_to_db(tender_id_long, publish_tender_response[0], tender_token,
                                            procurement_method, tender_status, number_of_lots)
        if add_tender_db[1] == 1:
            abort(500, '{}'.format(add_tender_db[0]))

        ''''# add documents to tender
        if add_documents == 1:
            add_documents = document.add_documents_to_tender_ds(tender_id_long, tender_token, list_of_id_lots)
        else:
            add_documents = 'tender was created without documents'''


        run_create_tender = bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method,
                                          list_of_id_lots, host_kit, 0)  # 0 - documents of bid

        print tender_id
        response_json['id'] = tender_id
        response_code = 0
        if received_tender_status == 'active.tendering':
            get_t_info = requests.get("{}/api/{}/tenders/{}".format(host_kit[0], host_kit[1], tender_id))
            response_json['id'] = tender_id
            if get_t_info.json()['data']['status'] == 'active.tendering':
                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                response_json['status'] = 'success'
                response_code = 201
            else:
                response_json['tenderStatus'] = get_t_info.json()['data']['status']
                response_json['status'] = 'error'
                response_code = 422

        if received_tender_status == 'active.pre-qualification':
            t_end_date = datetime.strptime(publish_tender_response[0].json()['data']['tenderPeriod']['endDate'], '%Y-%m-%dT%H:%M:%S+02:00')
            waiting_time = (t_end_date - datetime.now()).seconds
            print waiting_time
            time.sleep(waiting_time)
            qualif_counter = 0
            for x in range(5):
                qualif_counter += 1
                print qualif_counter
                get_t_info = requests.get("{}/api/{}/tenders/{}".format(host_kit[0], host_kit[1], tender_id))
                if get_t_info.json()['data']['status'] == 'active.pre-qualification':
                    response_json['tenderStatus'] = get_t_info.json()['data']['status']
                    response_json['status'] = 'success'
                    response_code = 201
                    break
                else:
                    if qualif_counter < 5:
                        time.sleep(60)
                        continue
                    else:
                        response_json['tenderStatus'] = get_t_info.json()['data']['status']
                        response_json['status'] = 'error'
                        response_code = 422

        add_tender_company = refresh.add_one_tender_company(company_id, platform_host, tender_id_long)
        response_json['tender_to_company'] = add_tender_company[0]

        return jsonify(response_json), response_code


        #db.session.remove()
        '''return jsonify({'data': {
            "tender": [{
                "publish_tender": publish_tender_response[1],
                "activate_tender": activate_tender[2],
                "add_tender_to_db": add_tender_db[0],
                # "documents_of_tender": add_documents,
                "add_tender_company": 0
            }],
            "bids": run_create_tender,
            "new_json": {
                "tenderID": tender_id
            }
        }
        }), 201'''
    elif procurement_method in below_threshold_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    elif procurement_method in limited_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    else:
        abort(400, 'Incorrect procurementMethodType')


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
        prequalification_result = qualification.select_my_bids(
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
    app.run(debug=True)
