# -*- coding: utf-8 -*-
from auctions.auction_validators import *
from tenders.tender_validators import *
from auctions import auction
from auctions import privatization
from datetime import timedelta
import core
from tools.pages import Pages
from flask import Flask, jsonify, request, make_response,\
    render_template, session, redirect, url_for, g, send_from_directory
from flask_httpauth import HTTPBasicAuth
import flask_login
from flask_cors import CORS, cross_origin
from admin import jquery_requests
from admin.pages import AdminPages
from user.pages import UserPages
from user.helper import *
from auctions.pages import AuctionPages
from tenders.pages import TenderPages
from tenders import monitoring
from tenders import tender_validators, tender
import hashlib
from language.translations import Translations, alert
from config import *

auth = HTTPBasicAuth()
app = Flask(__name__)
app.secret_key = os.urandom(32)
CORS(app)


# ############################################################ CUSTOM ERRORS ####################################################


def select_error_response(error, name, code):
    if 'response_error' in error.description:
        return make_response(jsonify(  # For response from CDB
            {'error': '{}'.format(name), 'description': error.description['response_error']}), code)
    elif '</' in error.description and '>' in error.description:
        return make_response(jsonify(  # For alerts
            {'error': '{}'.format(name), 'description': error.description}), code)
    else:
        content = render_template('page_error_x.html'.format(code), error_code=code, error_message=error.description)  # Select template
        return render_template('index.html', content=content, disable_sidebar=True, is_error_page=True), code


@app.errorhandler(400)
def custom400(error):
    return select_error_response(error, '400 Bad Request', 400)


@app.errorhandler(401)
def custom401(error):
    return select_error_response(error, '401 Unauthorized', 401)


@app.errorhandler(403)
def custom403(error):
    return select_error_response(error, '403 Forbidden', 403)


@app.errorhandler(404)
def custom404(error):
    return select_error_response(error, '404 Not Found', 404)


@app.errorhandler(405)
def custom405(error):
    return select_error_response(error, '405 Method Not Allowed', 405)


@app.errorhandler(415)
def custom415(error):
    return select_error_response(error, '415 Unsupported Media Type', 415)


@app.errorhandler(422)
def custom422(error):
    return select_error_response(error, '422 Unprocessable Entity', 422)


@app.errorhandler(500)
def custom500(error):
    return select_error_response(error, '500 Internal Server Error', 500)


@app.errorhandler(501)
def custom501(error):
    return select_error_response(error, '501 Not Implemented', 501)


@app.errorhandler(502)
def custom502(error):
    return select_error_response(error, '502 Bad Gateway', 502)


@app.errorhandler(503)
def custom503(error):
    return select_error_response(error, '503 Service Unavailable', 503)


# Get actual time for template
@app.context_processor
def global_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def global_user_data():
    user_data = dict()
    if 'username' in session:
        user_data['username'] = session['username']
        user_data['user_role_id'] = session['user_role']
        user_data['logged_in'] = session['logged_in']
    return user_data


@app.context_processor
def global_user_language():
    translation = dict()
    if 'user_id' in session:
        translation['lng'] = Translations(session['language'])  # core.get_user_language(session['user_id']) for get language with every request
    else:
        translation['lng'] = Translations('en')
    return translation


def get_user_role():
    user_role_id = Users.query.filter_by(user_login=session['username']).first().user_role_id
    db.session.remove()
    return user_role_id


def get_super_user_flag():
    super_user_flag = Users.query.filter_by(user_login=session['username']).first().super_user
    db.session.remove()
    return super_user_flag


def get_user_id():
    user_id = Users.query.filter_by(user_login=session['username']).first().id
    db.session.remove()
    return user_id


# Check session before every request
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=120)
    session.modified = True
    g.user = flask_login.current_user


# Generate template for Login form
def login_form():
    content = render_template('login.html')
    return render_template('index.html', content=content, disable_sidebar=True, disable_sign_in_link=True), 403


# Forbidden error for jquery requests
def jquery_forbidden_login():
    return abort(401, alert.error_401_unauthorized('alert_error_401_general'))


# Redirect to previous url
def redirect_url(default='main'):
    return request.args.get('next') or request.referrer or url_for(default)


# Generate session or show Login form
@app.route('/login', methods=['POST'])
def do_login():
    try:
        get_list_of_users = Users.query.all()
        list_of_users = []
        for user in range(len(get_list_of_users)):
            list_of_users.append(get_list_of_users[user].user_login)
        if request.form['username'] not in list_of_users:
            return redirect(redirect_url())
        else:
            user_id = Users.query.filter_by(user_login=request.form['username']).first().id
            user_password_db = Users.query.filter_by(id=user_id).first().user_password
            if hashlib.md5(request.form['password'].encode('utf8')).hexdigest() == user_password_db\
                    and Users.query.filter_by(id=user_id).first().active != 0:
                db.session.remove()
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['user_id'] = user_id
                session['user_role'] = get_user_role()
                session['super_user'] = get_super_user_flag()
                session['language'] = core.get_user_language(user_id)
                return redirect(redirect_url())
            else:
                return redirect(redirect_url())
    except Exception as e:
        abort(500, str(e))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('main'))


# Generate template for Main Page
@app.route("/")
def main():
    if not session.get('logged_in'):
        return login_form()
    else:
        content = render_template('main_page.html', list_of_tenders=0,
                                  list_of_types=list_of_procurement_types)
        return render_template('index.html', content=content)


# ################################################################ ADMIN ##############################################################
# #####################################################################################################################################
def check_if_admin():  # check if user is admin before generate a page
    if not session.get('logged_in'):
        return login_form()
    elif session['user_role'] != 1:
        return abort(403)
    else:
        return True


def check_if_admin_jquery():  # check if user is admin before accept jquery request
    if not session.get('logged_in'):
        return abort(401, alert.error_401_unauthorized('alert_error_401_general'))
    elif session['user_role'] != 1:
        return abort(403, alert.error_403_forbidden('alert_error_403_general'))
    else:
        return True


def check_if_superuser():
    if session['super_user'] == 1:
        return True
    else:
        return False


#                                                         ####### ADMIN PAGES ######
@app.route('/admin/<page>', methods=['GET'])  # generate custom page for admin
def admin_pages(page):
    if check_if_admin() is not True:
        return check_if_admin()
    admin_page = AdminPages
    if page == 'platforms':
        return admin_page.page_admin_platforms()
    elif page == 'users':
        return admin_page.page_admin_users(session)
    elif page == 'tenders':
        return admin_page.page_admin_tenders()
    elif page == 'auctions':
        return admin_page.page_admin_auctions()
    elif page == 'reports':
        return admin_page.page_admin_reports()
    else:
        return abort(404)


@app.route('/admin/reports/<report_id>', methods=['GET'])
def admin_report_view(report_id):
    if check_if_admin() is not True:
        return check_if_admin()
    else:
        return AdminPages.page_admin_report_view(report_id)


#                                                       ###### ADMIN JQUERY REQUESTS ######
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
        return jquery_requests.add_user(request, session)


# Delete platform/tender/auction/user (with jquery)
@app.route('/backend/jquery/<entity>/<entity_id>', methods=['DELETE'])
def jquery_delete_entity(entity, entity_id):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        if entity == 'platforms':
            return jquery_requests.delete_platform(entity_id)
        elif entity == 'tenders':
            return jquery_requests.delete_tender(entity_id)
        elif entity == 'auctions':
            return jquery_requests.delete_auction(entity_id)
        elif entity == 'users':
            return jquery_requests.delete_user(entity_id, check_if_superuser())


# Delete all tenders/auctions from database (with jquery)
@app.route('/backend/jquery/<entity>', methods=['DELETE'])
def jquery_delete_tenders(entity):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        if entity == 'tenders':
            return jquery_requests.delete_tenders()
        elif entity == 'auctions':
            return jquery_requests.delete_auctions()


# Delete report document (with jquery)
@app.route('/backend/jquery/report/files/<file_id>', methods=['DELETE'])
def jquery_delete_report_document(file_id):
    if check_if_admin_jquery() is not True:
        return check_if_admin_jquery()
    else:
        return jquery_requests.delete_report_file(file_id)

# ############################################################## ADMIN END #############################################################################

# ############################################################## MONITORINGS ##############################################################################


#                                                        ###### MONITORING PAGES ######
# Generate template for tender creation page
@app.route("/tenders/create-monitoring", methods=['GET'])
def page_create_monitoring():
    if not session.get('logged_in'):
        return login_form()
    else:
        return TenderPages.page_create_monitoring()


# ############################################################## TENDERS ##############################################################################
#                                                   ###### TENDER JQUERY REQUESTS ######


# Add one tender bid to company
@app.route('/api/tenders/bids/<bid_id>/company', methods=['PATCH'])
def add_tender_bid_to_company(bid_id):
    if not session.get('logged_in'):
        return abort(401, alert.error_401_unauthorized('alert_error_401_general'))
    else:
        if not request.form:
            abort(400, alert.error_400_bad_request('alert_error_400_no_form_submitted'))
        data = validator_add_tender_bid_to_company(bid_id, request.form)
        add_bid_company = core.add_one_bid_to_company(data['platform_host'], data['company-id'], bid_id, 'tender')
        if add_bid_company[1] == 201:
            return render_template('includes/bid_company_id.inc.html', company_id=data['company-id'], bid_platform=data['platform_host'])
        else:
            return jsonify(add_bid_company)


# Show all bids of tender
@app.route('/api/tenders/<tender_id_short>/bids', methods=['GET'])
def get_bids_of_one_tender(tender_id_short):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    else:
        validator_if_tender_id_short_in_db(tender_id_short)
        list_of_tender_bids = core.get_bids_of_entity(tender_id_short, 'tender')

        return render_template('modules/tender_modules/list_of_bids_of_tender.html', user_role_id=session['user_role'],
                               list_of_tender_bids=list_of_tender_bids, platforms=core.get_list_of_platforms(1))


#                                                        ###### TENDER PAGES ######
# Generate template for tender creation page
@app.route("/tenders/create-tender", methods=['GET'])
def page_create_tender():
    if not session.get('logged_in'):
        return login_form()
    else:
        return TenderPages.page_create_tender()


# Generate template for show page with list of bids for tender
@app.route("/tenders/bids", methods=['GET'])
def page_tender_bids():
    if not session.get('logged_in'):
        return login_form()
    else:
        return TenderPages.page_tender_bids()


# ############################################################## AUCTIONS ##############################################################################
#                                                   ###### AUCTION JQUERY REQUESTS ######
# Create tender/auction/privatization/monitoring
@app.route('/api/<entity>', methods=['POST'])
def create_entity_function(entity):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    if not request.form:
        abort(400, 'Form wasn\'t submitted')
    if entity == 'auctions':
        result = auction.create_auction(request.form, session)
    elif entity == 'privatization':
        result = privatization.create_privatization(request.form, session)
    elif entity == 'tenders':
        tender_validators.validator_create_tender(request.form)  # validate input data
        result = tender.creation_of_tender(request.form, session['user_id'])
    elif entity == 'monitorings':
        # tender_validators.validator_create_tender(request.form)  # validate input data
        result = monitoring.creation_of_monitoring(request.form, session['user_id'])
    else:
        result = 'ERROR', 422
    return jsonify(result[0]), result[1]


# Add one auction bid to company
@app.route('/api/auctions/bids/<bid_id>/company', methods=['PATCH'])
def add_auction_bid_to_company(bid_id):
    if not session.get('logged_in'):
        return abort(401, alert.error_401_unauthorized('alert_error_401_general'))
    else:
        if not request.form:
            abort(400, alert.error_400_bad_request('alert_error_400_no_form_submitted'))
        data = validator_add_auction_bid_to_company(bid_id, request.form)
        add_bid_company = core.add_one_bid_to_company(data['platform_host'], data['company-id'], bid_id, 'auction')
        if add_bid_company[1] == 201:
            return render_template('includes/bid_company_id.inc.html', company_id=data['company-id'], bid_platform=data['platform_host'])
        else:
            return jsonify(add_bid_company)


# Show all bids of auction
@app.route('/api/auctions/<auction_id_short>/bids', methods=['GET'])
def get_bids_of_one_auction(auction_id_short):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    else:
        validator_if_auction_id_short_in_db(auction_id_short)
        bids = core.get_bids_of_entity(auction_id_short, 'auction')
        return render_template('modules/auction_modules/list_of_bids_of_auction.html', user_role_id=session['user_role'],
                               list_of_auction_bids=bids, platforms=core.get_list_of_platforms(2))


#                                                        ###### AUCTION PAGES ######
# Generate template for auction creation page
@app.route("/auctions/create-auction", methods=['GET'])
def page_create_auction():
    if not session.get('logged_in'):
        return login_form()
    else:
        return AuctionPages.page_create_auction()


# Generate template for privatization creation page
@app.route("/auctions/create-privatization", methods=['GET'])
def page_create_privatization():
    if not session.get('logged_in'):
        return login_form()
    else:
        return AuctionPages.page_create_privatization()


# Generate template for show page with list of bids for auction
@app.route("/auctions/bids", methods=['GET'])
def page_auction_bids():
    if not session.get('logged_in'):
        return login_form()
    else:
        return AuctionPages.page_auction_bids()


# ############################################################## TOOLS ##############################################################################
#                                                       ###### TOOLS PAGES ######
@app.route('/tools/<page>', methods=['GET'])  # generate custom page for admin
def tools_pages(page):
    if not session.get('logged_in'):
        return login_form()
    pages = Pages()
    if page == 'json-viewer':
        return pages.page_json_viewer()
    else:
        return abort(404)


#                                                       ###### TOOLS JQUERY ######
# Get JSON of tender from CDB (with jquery) for json viewer
@app.route('/backend/jquery/get_tender_json/<tender_id>/<api_version>', methods=['GET'])
def jquery_get_tender_json(tender_id, api_version):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    else:
        return jsonify(jquery_requests.get_tender_json_from_cdb(tender_id, api_version)), 200


# ############################################################## USERS ##############################################################################
#                                                       ###### USER PAGES ######

# Open user preferences page
@app.route("/user/preferences", methods=['GET', 'POST'])
def page_user_preferences():
    if request.method == 'GET':
        if not session.get('logged_in'):
            return login_form()
        else:
            return UserPages(session).page_preferences()
    elif request.method == 'POST':
        if not session.get('logged_in'):
            return jquery_forbidden_login()
        else:
            if not request.form:
                abort(400, alert.error_400_bad_request('alert_error_400_no_form_submitted'))
            save_user_preferences(request.form, session)
            return UserPages(session).page_preferences()


# ############################################################## MODAL WINDOWS ##############################################################################
#                                                       ###### ADD REPORT WINDOW ######
@app.route("/modal/add_report", methods=['GET', 'POST'])
@cross_origin(resources=r'/modal/*')
def add_report():
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    if request.method == 'GET':
        return render_template('modal_windows/modal_add_report.html', report_types=core.get_list_of_report_types_as_object(),
                               report_priorities=core.get_list_of_report_priorities_as_object())
    else:
        if core.add_new_report(request, session):
            return render_template('modal_windows/modal_report_success.html', action='add')
        return jsonify('Something went wrong'), 400  # TODO Add template for Add report error


@app.route("/modal/edit_report/<report_id>", methods=['GET', 'PATCH'])
@cross_origin(resources=r'/modal/*')
def edit_report(report_id):
    if not session.get('logged_in'):
        return jquery_forbidden_login()
    report_data = core.get_report_info(report_id)
    if request.method == 'GET':
        return render_template('modal_windows/modal_edit_report.html',
                               report_types=core.get_list_of_report_types_as_object(),
                               report_priorities=core.get_list_of_report_priorities_as_object(),
                               report_statuses=core.get_list_of_report_statuses_as_object(),
                               report_data=report_data,
                               report_documents=core.get_report_documents(report_id))
    else:
        if core.save_edited_report(request, report_data):
            return render_template('modal_windows/modal_report_success.html', action='edit')
        return jsonify('Something went wrong'), 400  # TODO Add template for Edit report error


@app.route('/files/<entity>/<filename>', methods=['GET'])
def download_file(entity, filename):
    if not session.get('logged_in'):
        return login_form()
    if entity == 'report':
        return send_from_directory(REPORTS_DOCS_DIR, filename)
    else:
        return abort(404)


@app.route('/images/thumbnails/<entity>/<filename>', methods=['GET'])
def download_thumbnail(entity, filename):
    if not session.get('logged_in'):
        return login_form()
    if entity == 'report':
        return send_from_directory(REPORT_THUMBS_DIR, filename)
    else:
        return abort(404)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

# TODO Error alerts,
# TODO Translations and status/type/creator name instead of id on reports list page
# TODO Add validator to create monitoring page
