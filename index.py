# -*- coding: utf-8 -*-
from tenders.tender_additional_data import list_of_procurement_types, tender_status_list, list_of_api_versions
from database import db, Tenders, BidsTender, Users, Auctions, BidsAuction
from auctions import auction
from datetime import timedelta
import core
from flask import Flask, jsonify, request, abort, make_response, render_template, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import os
import flask
import flask_login
from flask_cors import CORS, cross_origin
from datetime import datetime
from admin import jquery_requests
from admin.pages import AdminPages
from auctions.pages import AuctionPages
from tenders import tender_validators, tender

auth = HTTPBasicAuth()
app = Flask(__name__,)
app.secret_key = os.urandom(32)
CORS(app)


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


@app.errorhandler(503)
def custom503(error):
    return make_response(jsonify(
        {'error': '503 Service Unavailable', 'description': error.description}), 503)
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


def get_user_id():
    user_id = Users.query.filter_by(user_login=session['username']).first().id
    db.session.remove()
    return user_id


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
            session['user_id'] = user_id
            session['user_role'] = get_user_role()
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
        content = render_template('tenders/create_tender.html', list_of_types=list_of_procurement_types, api_versions=list_of_api_versions, platforms=core.get_list_of_platforms(1),
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


# create tender
@app.route('/api/tenders', methods=['POST'])
@cross_origin(resources=r'/api/*')
def create_tender_function():
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    if not request.form:
        abort(400)
    tender_validators.validator_create_tender(request.form)  # validate input data
    result = tender.creation_of_tender(request.form, session['user_id'])
    return jsonify(result[0]), result[1]


# run synchronization (SQLA)
@app.route('/api/tenders/synchronization', methods=['PATCH'])
@auth.login_required
def update_list_of_tenders():
    update_tenders = core.update_tenders_list()
    db.session.close()
    if update_tenders[0] == 0:
        return jsonify({"status": "success", "updated tenders": update_tenders[1]})
    else:
        return jsonify({"status": "error", "description": str(update_tenders[1])})


# ##################################### BIDS #############################################
# show all bids of tender
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
        get_bids_of_tender = BidsTender.query.filter_by(tender_id=tender_id_long).all()
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
        return render_template('modules/tender_modules/list_of_bids_of_tender.html', user_role_id=get_user_role(), list_of_tender_bids=list_of_tender_bids, platforms=core.get_list_of_platforms(1))


# show all bids of auction
@app.route('/api/auctions/<auction_id_short>/bids', methods=['GET'])
def get_bids_of_one_auction(auction_id_short):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    else:
        list_of_auctions = Auctions.query.all()  # 'SELECT tender_id_long FROM tenders'???
        list_tid = []
        for tid in range(len(list_of_auctions)):
            list_tid.append(list_of_auctions[tid].auction_id_short)
        if auction_id_short not in list_tid:
            abort(404, 'Tender id was not found in database')  # ####################### add render template

        auction_id_long = Auctions.query.filter_by(auction_id_short=auction_id_short).first().auction_id_long
        get_bids_of_auction = BidsAuction.query.filter_by(auction_id=auction_id_long).all()
        list_of_auction_bids = []
        for every_bid in range(len(get_bids_of_auction)):
            bid_id = get_bids_of_auction[every_bid].bid_id
            bid_token = get_bids_of_auction[every_bid].bid_token
            bid_platform = get_bids_of_auction[every_bid].bid_platform
            user_identifier = get_bids_of_auction[every_bid].user_identifier
            company_id = get_bids_of_auction[every_bid].company_id
            added_to_site = get_bids_of_auction[every_bid].added_to_site

            list_of_auction_bids.append({"id": bid_id, "bid_token": bid_token,
                                        "user_identifier": user_identifier, "has_company": added_to_site, "bid_platform": bid_platform})
            if added_to_site == 1:
                list_of_auction_bids[every_bid]['company_id'] = company_id
                list_of_auction_bids[every_bid]['has_company'] = True
            else:
                list_of_auction_bids[every_bid]['has_company'] = False
        db.session.remove()
        return render_template('modules/auction_modules/list_of_bids_of_auction.html', user_role_id=get_user_role(), list_of_auction_bids=list_of_auction_bids, platforms=core.get_list_of_platforms(2))


# add one tender bid to company
@app.route('/api/tenders/bids/<bid_id>/company', methods=['PATCH'])
def add_tender_bid_to_company(bid_id):
    if not session.get('logged_in'):
        return abort(401)
    else:
        list_of_bids = BidsTender.query.all()
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
        add_bid_company = core.add_one_bid_to_company(company_platform_host, company_id, bid_id)
        db.session.commit()
        db.session.remove()
        if add_bid_company[1] == 201:
            return render_template('includes/bid_company_id.inc.html', company_id=company_id, bid_platform=company_platform_host)
        else:
            return jsonify(add_bid_company)


# add one auction bid to company
@app.route('/api/auctions/bids/<bid_id>/company', methods=['PATCH'])
def add_auction_bid_to_company(bid_id):
    if not session.get('logged_in'):
        return abort(401)
    else:
        list_of_bids = BidsAuction.query.all()
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
        add_bid_company = core.add_one_auction_bid_to_company(company_platform_host, company_id, bid_id)
        db.session.commit()
        db.session.remove()
        if add_bid_company[1] == 201:
            return render_template('includes/bid_company_id.inc.html', company_id=company_id, bid_platform=company_platform_host)
        else:
            return jsonify(add_bid_company)
# ################################################################ BIDS END ################################################################################


# ##################################################################################### ADMIN ##############################################################

def check_if_admin():  # check if user is admin before generate a page
    if not session.get('logged_in'):
        return login_form()
    elif session['user_role'] != 1:
        return abort(403, 'U r not allowed to access this page')
    else:
        return True


def check_if_admin_jquery():  # check if user is admin before accept jquery request
    if not session.get('logged_in'):
        return abort(401)
    elif session['user_role'] != 1:
        return abort(403, 'U r not allowed to access this page')
    else:
        return True


@app.route('/admin/<page>', methods=['GET'])  # generate page for admin
def admin_pages(page):
    if check_if_admin() is not True:
        return check_if_admin()
    admin_page = AdminPages(session['user_role'])
    if page == 'platforms':
        return admin_page.page_admin_platforms()
    elif page == 'users':
        return admin_page.page_admin_users()
    elif page == 'tenders':
        return admin_page.page_admin_tenders()
    elif page == 'json-viewer':
        return admin_page.page_admin_json_viewer()
    else:
        return abort(404)


# Add platform (with jquery)
@app.route('/backend/jquery/add_platform', methods=['POST'])
def jquery_add_platform():
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.add_platform(request)


# Add user (with jquery)
@app.route('/backend/jquery/add_user', methods=['POST'])
def jquery_add_user():
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.add_user(request)


# Delete platform (with jquery)
@app.route('/backend/jquery/platforms/<platform_id>', methods=['DELETE'])
def jquery_delete_platform(platform_id):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.delete_platform(platform_id)


# Delete tender (with jquery)
@app.route('/backend/jquery/tenders/<tender_id>', methods=['DELETE'])
def jquery_delete_tender(tender_id):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.delete_tender(tender_id)


# Get JSON of tender from CDB (with jquery) for json viewer
@app.route('/backend/jquery/get_tender_json/<tender_id>/<api_version>', methods=['GET'])
def jquery_get_tender_json(tender_id, api_version):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jsonify(jquery_requests.get_tender_json_from_cdb(tender_id, api_version)), 200
# ############################################################## ADMIN END #############################################################################


# ############################################################## AUCTIONS ##############################################################################
# ############################### JQUERY REQUESTS #####################################
# create auction
@app.route('/api/auctions', methods=['POST'])
@cross_origin(resources=r'/api/*')
def create_auction_function():
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    if not request.form:
        abort(400, 'Form wasn\'t submitted')
    result = auction.create_auction(request.form, session)
    return jsonify(result[0])


# ############################## PAGES ##################################################
# template for auction creation page
@app.route("/auctions/create-auction")
def page_create_auction():
    if not session.get('logged_in'):
        return login_form()
    else:
        return AuctionPages(session['user_role']).page_create_auction()


# template for work with tender bids
@app.route("/auctions/bids")
def page_auction_bids():
    if not session.get('logged_in'):
        return login_form()
    else:
        return AuctionPages(session['user_role']).page_auction_bids()


if __name__ == '__main__':
    app.run(debug=True, threaded=True)


# change existing platform
# @app.route('/api/tenders/platforms/<platform_id>', methods=['PATCH'])
# @auth.login_required
# def patch_platform(platform_id):
#     list_pid = []
#     list_of_platform_id = Platforms.query.all()
#     if platform_id.isdigit() is False:
#         abort(400, 'Platform_id must be number')
#     for pid in range(len(list_of_platform_id)):
#         list_pid.append(list_of_platform_id[pid].id)
#     if int(platform_id) not in list_pid:
#         abort(404, 'Platform id wasn\'t found in database')
#     if not request.json:  # check if json exists
#         abort(400, 'JSON was not found in request')
#     if 'data' not in request.json:  # check if data is in json
#         abort(400, 'Data was not found in request')
#     cp_request = request.json['data']
#     if 'platform_name' not in cp_request and 'platform_url' not in cp_request:
#         return jsonify({'data': {
#                             "status code": 202,
#                             "description": "Nothing was changed"
#                         }
#                         }), 202
#     platform_data = {}
#     if 'platform_name' in cp_request:
#         platform_data['platform_name'] = cp_request['platform_name']
#     if 'platform_url' in cp_request:
#         platform_url = cp_request['platform_url']
#         if validators.url(platform_url) is not True:
#             abort(400, 'URL is invalid')
#         else:
#             if platform_url[-1:] == '/':
#                 platform_url = platform_url[:-1]
#             platforms_url_list = Platforms.query.all()
#             list_platform_url = []
#             for url in range(len(platforms_url_list)):
#                 list_platform_url.append(platforms_url_list[url].platform_url)
#             actual_platform_url = Platforms.query.filter_by(id=platform_id).first().platform_url
#             print platform_url
#             print actual_platform_url
#             if platform_url in list_platform_url and platform_url != actual_platform_url:
#                 abort(422, 'URL exists in database')
#             platform_data['platform_url'] = platform_url
#     Platforms.query.filter_by(id=platform_id).update(platform_data)
#     db.session.commit()
#     db.session.remove()
#     return jsonify({"status": "success"}), 200
