import tenders.tender_additional_data
from database import *
from flask import render_template, abort, jsonify
import validators
import core
from auctions import auction_additional_data
from cdb_requests import TenderRequests, AuctionRequests
import hashlib
from config import *
from language.translations import alert
from os.path import isfile


def add_platform(request):
    if len(request.form['platform-name']) == 0:
        return abort(400, alert.error_404_not_found('alert_error_400_empty_platform_name'))
    if len(request.form['platform-url']) == 0:
        return abort(400, alert.error_404_not_found('alert_error_400_empty_platform_url'))

    if validators.url(request.form['platform-url']) is not True:
        abort(400, alert.error_404_not_found('alert_error_400_url_invalid'))

    if request.form['platform-url'][-1:] == '/':
        platform_url = request.form['platform-url'][:-1]
    else:
        platform_url = request.form['platform-url']

    platforms_url_list = Platforms.query.all()
    list_platform_url = []
    for url in range(len(platforms_url_list)):
        list_platform_url.append(platforms_url_list[url].platform_url)
    if platform_url in list_platform_url:
        abort(422, alert.error_404_not_found('alert_error_422_platform_exists_db'))

    platform_to_sql = Platforms(None, request.form['platform-name'], platform_url, int(request.form['platform_role']))
    db.session.add(platform_to_sql)
    last_id = Platforms.query.order_by(Platforms.id.desc()).first().id
    newly_added_platform_data = Platforms.query.filter_by(id=last_id)
    db.session.commit()
    db.session.remove()
    return render_template('includes/newly_added_platform_info.inc.html', platform=newly_added_platform_data, platform_roles=core.get_list_of_platform_roles())


def add_user(request, session):
    new_user_data = request.form
    if len(request.form['user-name']) < 4:
        return abort(400, alert.error_404_not_found('alert_error_400_username_min_length'))
    if len(request.form['user-password']) < 4:
        return abort(400, alert.error_404_not_found('alert_error_400_password_min_length'))
    all_users = core.get_list_of_users()
    list_login = []
    for x in range(len(all_users)):
        list_login.append(all_users[x].user_login)
    if request.form['user-name'] in list_login:
        return abort(422, alert.error_404_not_found('alert_error_422_user_exists'))

    psw = hashlib.md5(new_user_data['user-password'].encode('utf8')).hexdigest()
    user_to_sql = Users(None, new_user_data['user-name'], psw, new_user_data['user_role'], int(new_user_data['user_status']), None, None)
    db.session.add(user_to_sql)
    last_id = Users.query.order_by(Users.id.desc()).first().id
    newly_added_user_data = Users.query.filter_by(id=last_id)
    db.session.commit()
    db.session.remove()
    return render_template('includes/newly_added_user_info.inc.html', user=newly_added_user_data, user_roles=core.get_list_of_user_roles(),
                           super_user_flag=session['super_user'])


def delete_platform(platform_id):
    existing_platforms_id = []
    list_of_platforms_id_db = core.get_list_of_platforms()
    for x in range(len(list_of_platforms_id_db)):
        existing_platforms_id.append(str(list_of_platforms_id_db[x].id))
    if platform_id not in existing_platforms_id:
        return abort(404, alert.error_404_not_found('alert_error_404_no_platform_id'))
    Platforms.query.filter_by(id=platform_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_tender(tender_id):
    existing_tenders_id = []
    list_of_tenders_id_db = core.get_list_of_tenders()
    for x in range(len(list_of_tenders_id_db)):
        existing_tenders_id.append(str(list_of_tenders_id_db[x].id))
    if tender_id not in existing_tenders_id:
        return abort(404, alert.error_404_not_found('alert_error_404_no_tender_id'))
    tender_id_long = Tenders.query.filter_by(id=tender_id).first().tender_id_long
    BidsTender.query.filter_by(tender_id=tender_id_long).delete()
    Tenders.query.filter_by(id=tender_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_auction(auction_id):
    existing_auctions_id = []
    list_of_auctions_id_db = core.get_list_of_auctions()
    for x in range(len(list_of_auctions_id_db)):
        existing_auctions_id.append(str(list_of_auctions_id_db[x].id))
    if auction_id not in existing_auctions_id:
        return abort(404, alert.error_404_not_found('alert_error_404_no_auction_id'))
    auction_id_long = Auctions.query.filter_by(id=auction_id).first().auction_id_long
    BidsAuction.query.filter_by(auction_id=auction_id_long).delete()
    Auctions.query.filter_by(id=auction_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_user(user_id, is_superuser):
    existing_users_id = []
    list_of_users_id_db = core.get_list_of_users()
    for x in range(len(list_of_users_id_db)):
        existing_users_id.append(str(list_of_users_id_db[x].id))
    if user_id not in existing_users_id:
        return abort(404, alert.error_404_not_found('alert_error_404_no_user_id'))
    user_for_delete_role = Users.query.filter_by(id=user_id).first().user_role_id
    if user_for_delete_role == 1 and not is_superuser:
        return abort(403, alert.error_404_not_found('alert_error_403_not_allowed_delete_user'))
    elif Users.query.filter_by(id=user_id).first().super_user == 1:
        return abort(403, alert.error_404_not_found('alert_error_403_not_allowed_delete_superuser'))
    Users.query.filter_by(id=user_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_report_file(file_id):
    existing_files_id = []
    list_of_files_id_db = core.get_list_of_report_files()
    for x in range(len(list_of_files_id_db)):
        existing_files_id.append(str(list_of_files_id_db[x].id))
    if file_id not in existing_files_id:
        return abort(404, alert.error_404_not_found('alert_error_404_file_doesnt_exist'))
    filename = ReportDocuments.query.filter_by(id=file_id).first().filename
    original_file = os.path.join(REPORTS_DOCS_DIR, filename)
    try:
        if isfile(original_file):  # Check if original file exists
            # print('Original file exists: REMOVE ...')
            os.remove(original_file)  # Remove original file
        if original_file.endswith((".jpg", ".jpeg", ".png")):
            # print('Original file is an image, Check if thumbnail exists')
            if isfile(os.path.join(ROOT_DIR, REPORT_THUMBS_DIR, 'thumbnail_{}'.format(filename))):  # Check if thumbnail file exists
                # print('Thumbnail exists. REMOVE ...')
                os.remove(os.path.join(ROOT_DIR, REPORT_THUMBS_DIR, 'thumbnail_{}'.format(filename)))  # Remove thumbnail
    except Exception as e:
        print(str(e))
    ReportDocuments.query.filter_by(id=file_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_tenders():
    Tenders.query.delete()
    BidsTender.query.delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def delete_auctions():
    Auctions.query.delete()
    BidsAuction.query.delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200


def get_tender_json_from_cdb(tender_id, api_version):
    if api_version in tenders.tender_additional_data.list_of_api_versions:
        entity_json = TenderRequests(api_version).get_tender_info(tender_id).json()
    elif api_version in auction_additional_data.cdb_versions:
        entity_json = AuctionRequests(int(api_version)).get_auction_info(tender_id).json()
    else:
        entity_json = {"status": "error", "description": "unknown cdb version"}
    return entity_json
