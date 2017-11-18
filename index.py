# -*- coding: utf-8 -*-
import variables
import tender
import document
import bid
import json
import qualification
import time
import refresh
from flask import Flask, jsonify, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
import re


auth = HTTPBasicAuth()
app = Flask(__name__)


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
# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
# cursor = db.cursor()


@app.route('/')
def index():
    return "Main page"
# create tender example
'''data = {
    "data": {
        "procurementMethodType": "aboveThresholdEU",
        "number_of_lots": 2,
        "number_of_items": 3,
        "documents": 0,
        "number_of_bids": 3
    }
}'''


# create tender
@app.route('/api/tenders', methods=['POST'])
@auth.login_required
def create_tender_function():
    if not request.json:
        abort(400)
    try:
        request.json['data']
    except:
        abort(400, "Data was not found in request")
    tc_request = request.json['data']
    if 'procurementMethodType' not in tc_request or 'number_of_lots' not in tc_request \
            or 'number_of_items' not in tc_request or 'documents' not in tc_request \
            or 'number_of_bids' not in tc_request or 'accelerator' not in tc_request:
        abort(400, "One or more parameters are incorrect.")

    procurement_method = tc_request["procurementMethodType"]
    number_of_lots = tc_request["number_of_lots"]
    number_of_items = tc_request["number_of_items"]
    add_documents = tc_request["documents"]
    number_of_bids = tc_request["number_of_bids"]
    accelerator = tc_request["accelerator"]

    if type(number_of_lots) != int:
        abort(400, 'Number of lots must be integer')
    elif 0 > number_of_lots or number_of_lots > 10:
        abort(422, 'Number of lots must be between 0 and 10')

    if type(number_of_items) != int:
        abort(400, 'Number of items must be integer')
    elif 1 > number_of_items or number_of_items > 10:
        abort(422, 'Number of items must be between 1 and 10')

    if type(add_documents) != int:
        abort(400, 'Documents must be integer')
    elif 0 > add_documents or add_documents > 1:
        abort(422, 'Documents must be 0 or 1')

    if type(number_of_bids) != int:
        abort(400, 'Number of bids must be integer')
    elif 0 > number_of_bids or number_of_bids > 10:
        abort(422, 'Number of bids must be between 0 and 10')

    if type(accelerator) != int:
        abort(400, 'Accelerator must be integer')
    elif 1 > accelerator or accelerator > 15000:
        abort(422, 'Accelerator must be between 1 and 15000')
    # check procurement method
    if procurement_method in variables.above_threshold_procurement:
        list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)  # get list of id for lots
        # select type of tender (with or without lots)
        if number_of_lots == 0:
            json_tender = json.loads(tender.tender(number_of_lots, number_of_items, procurement_method, accelerator))
        else:
            json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                             procurement_method, accelerator))
        headers_tender = tender.headers_tender(json_tender)  # get headers for publish and activate tender

        # run publish tender function
        publish_tender_response = tender.publish_tender(headers_tender, json_tender)  # publish tender in draft status
        if publish_tender_response[1] == 1:
            abort(500, '{}'.format(publish_tender_response[0]))
        elif publish_tender_response[2] != 201:
            abort(publish_tender_response[2], json.loads(publish_tender_response[1]))

        # run activate tender function
        activate_tender = tender.activating_tender(publish_tender_response[0], headers_tender)  # activate tender
        if activate_tender[1] == 1:
            abort(500, '{}'.format(activate_tender[0]))
        elif activate_tender[2] != 200:
            abort(activate_tender[2], json.loads(activate_tender[1]))

        tender_id_long = publish_tender_response[0].headers['Location'].split('/')[-1]
        tender_token = publish_tender_response[0].json()['access']['token']
        tender_status = activate_tender[0].json()['data']['status']

        # add documents to tender
        if add_documents == 1:
            document.add_documents_to_tender(tender_id_long, tender_token)
        # add tender to database
        add_tender_db = tender.tender_to_db(tender_id_long, publish_tender_response[0], tender_token,
                                            procurement_method, tender_status, number_of_lots)
        if add_tender_db[1] == 1:
            abort(500, '{}'.format(add_tender_db[0]))

        run_create_tender = bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method,
                                          list_of_id_lots)
        return jsonify({'data': {
            "tender": [{
                "publish tender": publish_tender_response[1],
                "activate tender": activate_tender[1],
                "add tender to db": add_tender_db[0]
            }],
            "bids": run_create_tender

        }
        }), 201
    elif procurement_method in variables.below_threshold_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    elif procurement_method in variables.limited_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    else:
        abort(400, 'Incorrect procurementMethodType')


# run synchronization
@app.route('/api/tenders/synchronization', methods=['PATCH'])
@auth.login_required
def update_list_of_tenders():
    db = variables.database()
    cursor = db.cursor()
    update_tenders = refresh.update_tenders_list(cursor)
    db.commit()
    db.close()
    return jsonify({"status": "success", "updated tenders": update_tenders})


# get list of all tenders in local database
@app.route('/api/tenders', methods=['GET'])
def get_list_of_tenders():
    db = variables.database()
    cursor = db.cursor()
    list_of_tenders = refresh.get_tenders_list(cursor)
    db.commit()
    db.close()
    return jsonify({"data": {"tenders": list_of_tenders}})


# ########################## PREQUALIFICATIONS ###################################
# get list of tenders in prequalification status
@app.route('/api/tenders/prequalification', methods=['GET'])
def get_list_tenders_prequalification_status():
    db = variables.database()
    cursor = db.cursor()
    list_tenders_preq = refresh.get_tenders_prequalification_status(cursor)
    db.commit()
    db.close()
    list_json = []
    for x in range(len(list_tenders_preq)):
        id_tp = list_tenders_preq[x][0]
        procedure = list_tenders_preq[x][1]
        status = list_tenders_preq[x][2]
        list_json.append({"id": id_tp, "procurementMethodType": procedure, "status": status})
    return jsonify({'data': {"tenders": list_json}})


# pass prequalification for indicated tender
@app.route('/api/tenders/prequalification/<tender_id_long>', methods=['PATCH'])
@auth.login_required
def pass_prequalification(tender_id_long):
    check_tender_id = 'SELECT tender_id_long FROM tenders WHERE tender_id_long = "{}"'.format(tender_id_long)
    db = variables.database()
    cursor = db.cursor()
    cursor.execute(check_tender_id)
    if_tender_in_db = cursor.fetchall()
    if len(if_tender_in_db) == 0:
        abort(404)
    tender_token = qualification.get_tender_token(tender_id_long, cursor)  # get tender token
    qualifications = qualification.list_of_qualifications(tender_id_long)  # get list of qualifications for tender
    prequalification_result = qualification.select_my_bids(
        qualifications, tender_id_long, tender_token, cursor)  # approve all my bids
    time.sleep(2)
    finish_prequalification = qualification.finish_prequalification(
        tender_id_long, tender_token)  # submit prequalification protocol
    db.commit()
    db.close()
    return jsonify({'data': {"tenderID": tender_id_long, "prequalifications": prequalification_result,
                             "submit protocol": finish_prequalification}})


# add all tenders to company
@app.route('/api/tenders/company', methods=['POST'])
@auth.login_required
def all_tenders_to_company():
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    try:  # check if data is in json
        request.json['data']
    except:
        abort(400, 'Data was not found in request')
    tenders_to_company_request = request.json['data']
    if 'company_uid' not in tenders_to_company_request:  # check if company_id is in json
        abort(400, 'Company UID was not found in request')
    company_uid = tenders_to_company_request['company_uid']
    if type(company_uid) != int:
        abort(400, 'Company UID must be integer')
    db = variables.database()
    cursor = db.cursor()
    get_list_of_company_uid = "SELECT id FROM companies"
    cursor.execute(get_list_of_company_uid)
    list_of_company_uid = cursor.fetchall()
    list_of_uid = []
    for uid in range(len(list_of_company_uid)):
        list_of_uid.append(list_of_company_uid[uid][0])
    if company_uid in list_of_uid:
        get_company_id = "SELECT company_id, platform_id, company_role_id FROM companies WHERE id = {}"\
            .format(company_uid)
        cursor.execute(get_company_id)
        company_info = cursor.fetchone()
        company_id = company_info[0]
        platform_id = company_info[1]
        company_role_id = company_info[2]
        if company_role_id != 1:
            abort(422, 'Company role must be Buyer (1)')
        get_platform_url = "SELECT platform_url FROM platforms WHERE id = {}".format(platform_id)
        cursor.execute(get_platform_url)
        company_platform_host = cursor.fetchone()[0]
        add_tenders_to_company = refresh.add_all_tenders_to_company(cursor, company_id, company_platform_host)
        if add_tenders_to_company == 0:
            response_code = 200
        else:
            response_code = 201
        success_message = '{}{}'.format(add_tenders_to_company, ' tenders were added to company')
        db.commit()
        db.close()
        return jsonify({"status": "success", "description": success_message}), response_code
    else:
        error_no_uid = '{}{}{}'.format('Company with UID ', company_uid, ' was not found in database')
        print error_no_uid
        db.close()
        return jsonify({"status": "error", "description": error_no_uid})


@app.route('/api/tenders/<tender_id_long>/company', methods=['POST'])
@auth.login_required
def add_tender_to_company(tender_id_long):
    db = variables.database()
    cursor = db.cursor()
    list_of_tenders = 'SELECT tender_id_long FROM tenders'
    cursor.execute(list_of_tenders)
    list_of_id = cursor.fetchall()
    list_tid = []
    for tid in range(len(list_of_id)):
        list_tid.append(list_of_id[tid][0])
    if tender_id_long not in list_tid:
        abort(404, 'Tender id was not found in database')

    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    try:  # check if data is in json
        request.json['data']
    except:
        abort(400, 'Data was not found in request')
    tender_to_company_request = request.json['data']
    if 'company_uid' not in tender_to_company_request:  # check if company_id is in json
        abort(400, 'Company UID was not found in request')
    company_uid = tender_to_company_request['company_uid']
    if type(company_uid) != int:
        abort(400, 'Company UID must be integer')

    get_list_of_company_uid = "SELECT id FROM companies"
    cursor.execute(get_list_of_company_uid)
    list_of_company_uid = cursor.fetchall()
    list_of_uid = []
    for uid in range(len(list_of_company_uid)):
        list_of_uid.append(int(list_of_company_uid[uid][0]))
    if company_uid not in list_of_uid:
        abort(422, 'Company was not found in database')
    get_company_id = "SELECT company_id, platform_id, company_role_id FROM companies WHERE id = {}".format(company_uid)
    cursor.execute(get_company_id)
    company_info = cursor.fetchone()
    company_id = company_info[0]
    platform_id = company_info[1]
    company_role_id = company_info[2]
    if company_role_id != 1:
        abort(422, 'Company role must be Buyer (1)')
    get_platform_url = "SELECT platform_url FROM platforms WHERE id = {}".format(platform_id)
    cursor.execute(get_platform_url)
    company_platform_host = cursor.fetchone()[0]
    add_tender_company = refresh.add_one_tender_to_company(cursor, company_id, company_platform_host, tender_id_long)
    db.commit()
    db.close()
    if add_tender_company[1] == 201:
        return jsonify(add_tender_company[0]), 201
    else:
        return jsonify(add_tender_company)


# Add new company in database
@app.route('/api/tenders/companies', methods=['POST'])
@auth.login_required
def create_company():
    if not request.json:  # check if json exists
        abort(400, 'JSON was not found in request')
    try:  # check if data is in json
        request.json['data']
    except:
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
    if type(company_identifier) not in [int, long]:
        abort(400, 'Company Identifier must be integer')
    if len(str(company_identifier)) not in [8, 10]:
        abort(422, 'Company Identifier must be 8 or 10 characters long')
    if type(platform_id) != int:
        abort(400, 'Platform ID must be integer')

    db = variables.database()
    cursor = db.cursor()
    check_company_role_id = 'SELECT id FROM roles'
    cursor.execute(check_company_role_id)
    list_of_roles_id = cursor.fetchall()
    list_roles = []
    for rid in range(len(list_of_roles_id)):
        list_roles.append(int(list_of_roles_id[rid][0]))
    if company_role_id not in list_roles:
        abort(422, 'Role wasn\'t found in database')

    check_platform_id = 'SELECT id FROM platforms'
    cursor.execute(check_platform_id)
    list_of_platform_id = cursor.fetchall()
    list_platforms_id = []
    for pid in range(len(list_of_platform_id)):
        list_platforms_id.append(int(list_of_platform_id[pid][0]))
    if platform_id not in list_platforms_id:
        abort(422, 'Platform ID wasn\'t found in database')
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", company_email):
        abort(400, 'Email address is invalid')

    get_company_id_platform = "SELECT company_id, platform_id FROM companies"
    cursor.execute(get_company_id_platform)
    company_platform_id_combination = cursor.fetchall()
    combinations = []
    for combination in range(len(company_platform_id_combination)):
        comp_id = company_platform_id_combination[combination][0]
        pl_id = company_platform_id_combination[combination][1]
        combinations.append([comp_id, pl_id])
    if [company_id, platform_id] in combinations:
        abort(422, "Company with this ID was added to this platform before")
    add_company = "INSERT INTO companies VALUES(null, '{}', '{}', '{}', '{}', '{}')".format(
        company_email, company_id, company_role_id, platform_id, company_identifier)
    cursor.execute(add_company)
    get_company_uid = "SELECT id FROM companies WHERE company_id = '{}' AND platform_id = '{}'".format(company_id,
                                                                                                       platform_id)
    cursor.execute(get_company_uid)
    uid = cursor.fetchone()[0]
    db.commit()
    db.close()
    return jsonify({'status': 'success', 'id': int('{}'.format(uid))})


if __name__ == '__main__':
    app.run(debug=True)
