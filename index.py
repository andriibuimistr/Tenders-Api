# -*- coding: utf-8 -*-
from variables import Companies, Platforms, Roles, Tenders, Bids, db, above_threshold_procurement, below_threshold_procurement, limited_procurement, tender_status_list,\
    without_pre_qualification_procedures, prequalification_procedures, competitive_procedures, without_pre_qualification_procedures_status, prequalification_procedures_status, \
    competitive_procedures_status, competitive_dialogue_eu_status, below_threshold_status, create_tender_required_fields, limited_status, list_of_procurement_types, list_of_api_versions, platforms,\
    statuses_with_high_acceleration, negotiation_procurement, statuses_negotiation_with_high_acceleration, Users
import tender
# import document
from datetime import timedelta
import qualification
import time
import refresh
from refresh import get_tenders_list
from flask import Flask, jsonify, request, abort, make_response, render_template, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import re
import validators
import os
import flask
import flask_login
from flask_cors import CORS, cross_origin
from datetime import datetime
from admin import jquery_requests
from admin.pages import AdminPages

auth = HTTPBasicAuth()
app = Flask(__name__,)
app.secret_key = os.urandom(32)
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


#############################################################################################
##########################################################

# actual time for template
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


def get_user_role():
    user_role_id = Users.query.filter_by(user_login=session['username']).first().user_role_id
    db.session.remove()
    return user_role_id


@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=120)
    flask.session.modified = True
    flask.g.user = flask_login.current_user


def login_form():
    return render_template('login.html'), 403


def jquery_forbidden_login():
    return abort(403, "You are not logged in")


def redirect_url(default='main'):
    return request.args.get('next') or request.referrer or url_for(default)


@app.route('/login', methods=['POST'])
def do_login():
    get_list_of_users = Users.query.all()
    list_of_users = []
    for user in range(len(get_list_of_users)):
        list_of_users.append(get_list_of_users[user].user_login)
    if request.form['username'] not in list_of_users:
        return redirect(redirect_url())
    else:
        user_id = Users.query.filter_by(user_login=request.form['username']).first().id
        if request.form['password'] == Users.query.filter_by(id=user_id).first().user_password and Users.query.filter_by(id=user_id).first().active != 0:
            db.session.remove()
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(redirect_url())
        else:
            return redirect(redirect_url())


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('main'))


# main page
@app.route("/")
def main():
    if not session.get('logged_in'):
        return login_form()
    else:
        content = render_template('main_page.html', list_of_tenders=0, list_of_types=list_of_procurement_types)
        # user_role_id = Users.query.filter_by(user_login=session['username']).first().user_role_id
        return render_template('index.html', user_role_id=get_user_role(), content=content)


# template for tender creation page
@app.route("/tenders/create-tender")
def page_create_tender():
    if not session.get('logged_in'):
        return login_form()
    else:
        content = render_template('tenders/create_tender.html', list_of_types=list_of_procurement_types, api_versions=list_of_api_versions, platforms=refresh.get_list_of_platforms(1),
                                  statuses=tender_status_list)
        return render_template('index.html', user_role_id=get_user_role(), content=content)


# template for work with tender bids
@app.route("/tenders/bids")
def page_tender_bids():
    if not session.get('logged_in'):
        return login_form()
    else:
        content = render_template('tenders/tender_bids.html')
        # user_role_id = Users.query.filter_by(user_login=session['username']).first().user_role_id
        return render_template('index.html', user_role_id=get_user_role(), content=content)

##############################################################################################################################################
######################################################################################

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def index(path):
#     return render_template('index.html')


# create tender
@app.route('/api/tenders', methods=['POST'])
@cross_origin(resources=r'/api/*')
def create_tender_function():
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    if not request.form:
        abort(400)
    # if 'data' not in request.json:  # check if data is in json
    #     abort(400, 'Data was not found in request')
    tc_request = request.form
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
    received_tender_status = tc_request['tenderStatus']
    api_version = tc_request['api_version']
    platform_host = tc_request['platform_host']

    if str(number_of_lots).isdigit() is False:
        abort(400, 'Number of lots must be integer')
    elif 0 > int(number_of_lots) or int(number_of_lots) > 20:
        abort(422, 'Number of lots must be between 0 and 20')

    if str(number_of_items).isdigit() is False:
        abort(400, 'Number of items must be integer')
    elif 1 > int(number_of_items) or int(number_of_items) > 20:
        abort(422, 'Number of items must be between 1 and 20')

    '''if type(add_documents) != int:
        abort(400, 'Documents must be integer')
    elif 0 > add_documents or add_documents > 1:
        abort(422, 'Documents must be 0 or 1')

    if type(documents_of_bid) != int:
        abort(400, 'Documents of bid must be integer')
    elif 0 > documents_of_bid or documents_of_bid > 1:
        abort(422, 'Documents of bid must be 0 or 1')'''

    if str(number_of_bids).isdigit() is False:
        abort(400, 'Number of bids must be integer')
    elif 0 > int(number_of_bids) or int(number_of_bids) > 10:
        abort(422, 'Number of bids must be between 0 and 10')

    if str(accelerator).isdigit() is False:
        abort(400, 'Accelerator must be integer')
    elif 1 > int(accelerator) or int(accelerator) > 30000:
        abort(422, 'Accelerator must be between 1 and 30000')

    if str(company_id).isdigit() is False:
        abort(400, 'Company ID must be integer')
    if int(company_id) == 0:
        abort(422, 'Company id can\'t be 0')

    if received_tender_status not in tender_status_list:
        return abort(422, 'Tender status must be one of: {}'.format(tender_status_list))
    if api_version not in list_of_api_versions:
        return abort(422, 'API version must be one of: {}'.format(list_of_api_versions))
    if platform_host not in platforms:
        return abort(422, 'Platform must be one of: {}'.format(platforms))

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
                    return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status))
            else:
                if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status + competitive_dialogue_eu_status:
                    return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status +
                                                                                  competitive_dialogue_eu_status))
    elif procurement_method in below_threshold_procurement:  # create below threshold procedure
        if received_tender_status not in below_threshold_status:
            abort(422, "For '{}' status must be one of: {}".format(procurement_method, below_threshold_status))
    elif procurement_method in limited_procurement:  # create limited procedure
        if received_tender_status not in limited_status:
            abort(422, "For '{}' status must be one of: {}".format(procurement_method, limited_status))
    else:  # incorrect procurementMethodType
        abort(422, 'procurementMethodType must be one of: {}'.format(above_threshold_procurement + below_threshold_procurement + limited_procurement))

    if int(accelerator) < 30:
        if received_tender_status not in statuses_with_high_acceleration:
            abort(422, 'Accelerator value can be less than 30 for the following statuses only: {}'.format(statuses_with_high_acceleration))
        if procurement_method in negotiation_procurement and received_tender_status not in statuses_negotiation_with_high_acceleration:
            abort(422, 'Accelerator value can be less than 30 for: {} for the following statuses only: {}'.format(negotiation_procurement, statuses_negotiation_with_high_acceleration))
        if procurement_method == 'belowThreshold' and received_tender_status != 'active.enquiries':
            abort(422, 'For {} accelerator value can be less than 30 for the following status only: {}'.format('"belowThreshold"', 'active.enquiries'))

    tc_request = {"procurementMethodType": procurement_method,
                  "number_of_lots": int(number_of_lots),
                  "number_of_items": int(number_of_items),
                  "number_of_bids": int(number_of_bids),
                  "accelerator": int(accelerator),
                  "company_id": int(company_id),
                  "platform_host": platform_host,
                  "api_version": api_version,
                  "tenderStatus": received_tender_status}
    result = tender.creation_of_tender(tc_request)
    return jsonify(result[0]), result[1]


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
    return jsonify({"data": {"tenders": list_of_tenders[1]}})


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
@app.route('/api/tenders/<tender_id_short>/bids', methods=['GET'])
def get_bids_of_one_tender(tender_id_short):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    else:
        list_of_tenders = Tenders.query.all()  # 'SELECT tender_id_long FROM tenders'???
        list_tid = []
        for tid in range(len(list_of_tenders)):
            list_tid.append(list_of_tenders[tid].tender_id_short)
        if tender_id_short not in list_tid:
            abort(404, 'Tender id was not found in database')  # ####################### add render template

        tender_id_long = Tenders.query.filter_by(tender_id_short=tender_id_short).first().tender_id_long
        get_bids_of_tender = Bids.query.filter_by(tender_id=tender_id_long).all()
        list_of_tender_bids = []
        for every_bid in range(len(get_bids_of_tender)):
            bid_id = get_bids_of_tender[every_bid].bid_id
            bid_token = get_bids_of_tender[every_bid].bid_token
            bid_platform = get_bids_of_tender[every_bid].bid_platform
            user_identifier = get_bids_of_tender[every_bid].user_identifier
            company_id = get_bids_of_tender[every_bid].company_id
            added_to_site = get_bids_of_tender[every_bid].added_to_site

            list_of_tender_bids.append({"id": bid_id, "bid_token": bid_token,
                                        "user_identifier": user_identifier, "has_company": added_to_site, "bid_platform": bid_platform})
            if added_to_site == 1:
                list_of_tender_bids[every_bid]['company_id'] = company_id
                list_of_tender_bids[every_bid]['has_company'] = True
            else:
                list_of_tender_bids[every_bid]['has_company'] = False
        db.session.remove()
        return render_template('modules/tender_modules/list_of_bids_of_tender.html', user_role_id=get_user_role(), list_of_tender_bids=list_of_tender_bids, platforms=refresh.get_list_of_platforms(1))


# add one bid to company (SQLA)
@app.route('/api/tenders/bids/<bid_id>/company', methods=['PATCH'])
def add_bid_to_company(bid_id):
    if not session.get('logged_in'):
        return abort(401)
    else:
        list_of_bids = Bids.query.all()
        list_bid = []
        for tid in range(len(list_of_bids)):
            list_bid.append(list_of_bids[tid].bid_id)
        if bid_id not in list_bid:
            abort(404, 'Bid id was not found in database')

        if not request.form:
            abort(400)
        bid_to_company_data = request.form

        if 'company-id' not in bid_to_company_data:
            abort(400, 'Company UID was not found in request')

        if str(request.form['company-id']).isdigit() is False:
            abort(400, 'Company UID must be integer')

        if int(request.form['company-id']) == 0:
            abort(422, 'Company id can\'t be 0')

        company_id = request.form['company-id']

        company_platform_host = request.form['platform_host']
        add_bid_company = refresh.add_one_bid_to_company(company_platform_host, company_id, bid_id)
        db.session.commit()
        db.session.remove()
        if add_bid_company[1] == 201:
            return render_template('includes/bid_company_id.inc.html', company_id=company_id, bid_platform=company_platform_host)
        else:
            return jsonify(add_bid_company)


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


# ##################################################################################### ADMIN ##############################################################

def check_if_admin():
    if not session.get('logged_in'):
        return login_form()
    elif get_user_role() != 1:
        return abort(403, 'U r not allowed to access this page')
    else:
        return True


def check_if_admin_jquery():
    if not session.get('logged_in'):
        return abort(401)
    elif get_user_role() != 1:
        return abort(403, 'U r not allowed to access this page')
    else:
        return True


@app.route('/admin/<page>', methods=['GET'])
def admin_pages(page):
    if check_if_admin() is not True:
        return check_if_admin()
    if page == 'platforms':
        return AdminPages(1).page_admin_platforms()
    elif page == 'users':
        return AdminPages(1).page_admin_users()
    else:
        return abort(404)


# Add platform (with jquery)
@app.route('/backend/jquery/add_platform', methods=['POST'])
def jquery_add_platform():
    if not session.get('logged_in'):
        return check_if_admin_jquery()
    else:
        return jquery_requests.add_platform(request)


# Add platform (with jquery)
@app.route('/backend/jquery/add_user', methods=['POST'])
def jquery_add_user():
    if check_if_admin() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.add_user(request)


# Delete platform (with jquery)
@app.route('/backend/jquery/platforms/<platform_id>', methods=['DELETE'])
def jquery_delete_platform(platform_id):
    if not session.get('logged_in'):
        return check_if_admin_jquery()
    else:
        return jquery_requests.delete_platform(platform_id)
# ############################################################## ADMIN END #############################################################################


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
