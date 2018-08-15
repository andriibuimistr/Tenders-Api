# -*- coding: utf-8 -*-
from database import *
import sys
from tenders.data_for_tender import activate_contract_json
from cdb_requests import *
from document import *
import binascii
from config import *
from sqlalchemy import asc, desc
from PIL import Image
from os.path import isfile, join
from resizeimage import resizeimage


def get_random_32():
    return str(binascii.hexlify(os.urandom(16)))


def time_counter(waiting_time, message=''):
    for remaining in range(waiting_time, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining to {}".format(remaining, message))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rWaiting time is over!\n")


def add_one_tender_company(company_id, company_platform_host, entity_id_long, entity_token, entity):
    if entity == 'tender':
        get_tender_data = Tenders.query.filter_by(tender_id_long=entity_id_long).first()
        db.session.remove()
    else:
        get_tender_data = Auctions.query.filter_by(auction_id_long=entity_id_long).first()
        db.session.remove()
    added_to_site = get_tender_data.added_to_site

    if added_to_site == 0 or added_to_site is None:
        response = None
        add_count = 0
        for x in range(30):
            add_count += 1
            print("Adding {} to company. Attempt {}".format(entity, add_count))
            try:
                add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(company_platform_host, '/tender/add-tender-to-company?tid=', entity_id_long, '&token=', entity_token, '&company=', company_id,
                                                                     '&acc_token=SUPPPER_SEEECRET_STRIIING'))
                add_to_site_response = add_to_site.json()
                if type(add_to_site_response) == int and entity == 'auction':
                    Auctions.query.filter_by(auction_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    print('\nAuction was added to site - ' + entity_id_long)
                    response = {'status': 'success'}, 201
                    break
                if 'tid' in add_to_site_response:
                    Tenders.query.filter_by(tender_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    db.session.commit()
                    db.session.remove()
                    print('\nTender was added to site - ' + entity_id_long)
                    response = {'status': 'success'}, 201, add_to_site_response['tid']
                    break
                elif 'tender has company' in add_to_site_response['error']:
                    if entity == 'tender':
                        Tenders.query.filter_by(tender_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    elif entity == 'auction':
                        Auctions.query.filter_by(auction_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    response = {'status': '{} has company'.format(entity)}, 201, add_to_site_response['tid']
                    print('{} has company'.format(entity))
                    break
                else:
                    print('{}{}{}'.format(entity_id_long, ' - ', add_to_site_response))
                    if add_count < 30:
                        time.sleep(20)
                        continue
                    else:
                        abort(422, add_to_site_response)
            except ConnectionError as e:
                print('Connection Error')
                if add_count < 30:
                    time.sleep(1)
                    continue
                else:
                    abort(503, 'Publish {} error: {}'.format(entity, str(e)))
            except Exception as e:
                if add_count < 30:
                    time.sleep(1)
                    continue
                else:
                    abort(500, 'Publish {} error: {}'.format(entity, str(e)))
        return response
    else:
        print('{} {}{}'.format(entity, entity_id_long, ' was added to company before'))
        return abort(422, '{} was added to site before'.format(entity))


# ################################### BIDS ############################
# add one bid to company (SQLA)
def add_one_bid_to_company(company_platform_host, company_id, bid_id, entity):
    if entity == 'tender':
        get_bid_data = BidsTender.query.filter_by(bid_id=bid_id).first()
        tender_id = get_bid_data.tender_id
    else:
        get_bid_data = BidsAuction.query.filter_by(bid_id=bid_id).first()
        tender_id = get_bid_data.auction_id
    bid_id = get_bid_data.bid_id
    bid_token = get_bid_data.bid_token
    added_to_site = get_bid_data.added_to_site

    if added_to_site == 0 or added_to_site is None:
        add_count = 0
        for x in range(30):
            add_count += 1
            print("Adding bid to company. Attempt {}".format(add_count))
            try:
                add_to_site = requests.get('{}{}{}{}{}{}{}{}{}{}'.format(
                    company_platform_host, '/tender/add-bid-to-company?tid=', tender_id, '&bid=', bid_id, '&token=', bid_token, '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
                add_to_site_response = add_to_site.json()
                if 'tid' in add_to_site_response and add_to_site.status_code == 200:
                    if entity == 'tender':
                        BidsTender.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    else:
                        BidsAuction.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    db.session.commit()
                    db.session.remove()
                    print('\nBid was added to company - ' + bid_id)
                    print('{}{}'.format('Tender ID is: ', add_to_site_response['tid']))
                    return {'status': 'success'}, 201
                elif 'Bid exist' in add_to_site_response['error']:
                    if entity == 'tender':
                        BidsTender.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    else:
                        BidsAuction.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    db.session.commit()
                    db.session.remove()
                    print('Bid has company')
                    abort(422, 'Bid has company')
                else:
                    print('{}{}{}'.format(bid_id, ' - ', add_to_site_response))
                    return {'status': 'error', 'description': add_to_site_response}
            except Exception as e:
                if add_count < 30:
                    time.sleep(1)
                    continue
                else:
                    abort(500, 'Publish {} error: ' + str(e))
    else:
        print('{}{}{}'.format('Bid ', bid_id, ' was added to company before'))
        abort(422, 'Bid was added to company before')


def get_bids_of_entity(id_short, entity):
    if entity == 'tender':
        id_long = Tenders.query.filter_by(tender_id_short=id_short).first().tender_id_long
        bids = BidsTender.query.filter_by(tender_id=id_long).all()
    else:
        id_long = Auctions.query.filter_by(auction_id_short=id_short).first().auction_id_long
        bids = BidsAuction.query.filter_by(auction_id=id_long).all()
    list_of_bids = []
    for every_bid in range(len(bids)):
        added_to_site = bids[every_bid].added_to_site
        list_of_bids.append({"id": bids[every_bid].bid_id, "bid_token": bids[every_bid].bid_token, "user_identifier": bids[every_bid].user_identifier, "has_company": added_to_site,
                             "bid_platform": bids[every_bid].bid_platform})

        if added_to_site == 1:
            list_of_bids[every_bid]['company_id'] = bids[every_bid].company_id
            list_of_bids[every_bid]['has_company'] = True
        else:
            list_of_bids[every_bid]['has_company'] = False
    db.session.remove()
    return list_of_bids


# get list of platform ()
def get_list_of_platforms(platform_role=False):
    if platform_role:  # if platform role is passed to function
        platforms_list = Platforms.query.filter_by(platform_role=platform_role).all()
    else:
        platforms_list = Platforms.query.all()
    db.session.remove()
    return platforms_list


# get list of platform roles
def get_list_of_platform_roles():
    platform_roles = PlatformRoles.query.all()
    db.session.remove()
    roles_dict = dict()
    for platform_role in range(len(platform_roles)):
        roles_dict[platform_roles[platform_role].id] = platform_roles[platform_role].platform_role_name
    return roles_dict


# get list of platform URLs
def get_list_of_platform_urls(platform_role):
    platforms = Platforms.query.filter_by(platform_role=platform_role).all()
    db.session.remove()
    urls_list = []
    for number in range(len(platforms)):
        urls_list.append(platforms[number].platform_url)
    return urls_list


# get list of user
def get_list_of_users():
    users_list = Users.query.all()
    db.session.remove()
    return users_list


# get list of user roles
def get_list_of_user_roles():
    user_roles = Roles.query.all()
    db.session.remove()
    roles_dict = dict()
    for user_role in range(len(user_roles)):
        roles_dict[user_roles[user_role].id] = user_roles[user_role].role_name
    return roles_dict


# get list of report types
def get_list_of_report_types():
    report_types = ReportTypes.query.all()
    db.session.remove()
    types_dict = dict()
    for report_type in range(len(report_types)):
        types_dict[report_types[report_type].id] = report_types[report_type].name
    return types_dict


# get list of user
def get_list_of_report_files():
    files_list = ReportDocuments.query.all()
    db.session.remove()
    return files_list


# get list of report types as object
def get_list_of_report_types_as_object():
    report_types = ReportTypes.query.all()
    db.session.remove()
    return report_types


# get list of report types
def get_list_of_report_statuses():
    report_statuses = ReportStatus.query.all()
    db.session.remove()
    statuses_dict = dict()
    for report_status in range(len(report_statuses)):
        statuses_dict[report_statuses[report_status].id] = report_statuses[report_status].name
    return statuses_dict


# get list of report priorities
def get_list_of_report_priorities():
    report_priorities = ReportPriorities.query.all()
    db.session.remove()
    priorities_dict = dict()
    for report_priority in range(len(report_priorities)):
        priorities_dict[report_priorities[report_priority].id] = report_priorities[report_priority].name
    return priorities_dict


# get list of report priorities as object
def get_list_of_report_priorities_as_object():
    report_priorities = ReportPriorities.query.all()
    db.session.remove()
    return report_priorities


# get list of report statuses as object
def get_list_of_report_statuses_as_object():
    report_statuses = ReportStatus.query.all()
    db.session.remove()
    return report_statuses


def get_list_of_tenders():
    tenders_list = Tenders.query.order_by(desc(Tenders.id)).all()  # from last to first
    db.session.remove()
    return tenders_list


def get_list_of_auctions():
    auctions_list = Auctions.query.order_by(desc(Auctions.id)).all()  # from last to first (can de just "id desc" instead of desc(Auctions.id))
    db.session.remove()
    return auctions_list


def get_list_of_reports():
    reports_list = Reports.query.order_by(asc(Reports.id)).all()  # from first to last
    db.session.remove()
    return reports_list


# get list of platform (SQLA)
def get_list_of_languages():
    languages_list = Languages.query.all()
    db.session.remove()
    return languages_list


def get_user_language(user_id):
    user_lang_id = Users.query.filter_by(id=user_id).first().user_lang_id
    languages = Languages.query.all()
    list_of_languages = list()
    for lang in range(len(languages)):
        list_of_languages.append(languages[lang].id)
    if user_lang_id not in list_of_languages:
        user_lang_id = 2
    language_system_name = Languages.query.filter_by(id=user_lang_id).first().system_name
    db.session.remove()
    return language_system_name


def get_report_info(report_id):
    report = Reports.query.filter_by(id=report_id).first()
    db.session.remove()
    return report


def get_report_documents(report_id):
    report_id_long = Reports.query.filter_by(id=report_id).first().id_long
    report_docs = ReportDocuments.query.filter_by(related_report_id=report_id_long).all()
    db.session.remove()
    return report_docs


def get_report_images(report_id):
    report_id_long = Reports.query.filter_by(id=report_id).first().id_long
    report_docs = ReportDocuments.query.filter_by(related_report_id=report_id_long).all()
    db.session.remove()
    report_img_thumbnails = list()
    for every_file in report_docs:
        fn = every_file.filename
        # print fn
        filepath = join(REPORTS_DOCS_DIR, fn)
        if isfile(join(filepath)):  # Check if original file exists
            if fn.endswith((".jpg", ".jpeg", ".png")):  # Check if file is an image
                thumbnail = join(ROOT_DIR, REPORT_THUMBS_DIR, 'thumbnail_{}'.format(fn))
                if not isfile(thumbnail):  # Check if file's thumbnail wasn't created
                    # print 'Generate file: {}'.format('thumbnail_{}'.format(fn))
                    # o_img = open(filepath, 'r')  # Open original image file
                    img = Image.open(filepath)
                    img = resizeimage.resize_cover(img, [200, 120])
                    if not os.path.exists(os.path.dirname(thumbnail)):
                        os.makedirs(os.path.dirname(thumbnail))
                    img.save(thumbnail, img.format)  # Save thumbnail into report images directory
                    img.close()
                report_img_thumbnails.append({"thumb_path": '/images/thumbnails/report/thumbnail_{}'.format(fn),
                                              "title": every_file.original_filename,
                                              "path": '/files/report/{}'.format(fn)})
    return report_img_thumbnails


def check_if_contract_exists(get_t_info):
    try:
        if get_t_info.json()['data']['contracts']:
            return 200
    except Exception as e:
        print(e)
        return e


def get_time_difference(api_version, entity=''):
    lt = int(time.mktime(datetime.utcnow().timetuple()))
    if entity == 'lots':
        r = Privatization(entity).get_list_of_lots()
    elif entity == 'monitoring':
        r = Monitoring(api_version).get_list_of_monitorings()
    else:
        r = TenderRequests(api_version).get_list_of_tenders()
    st = int(time.mktime(datetime.strptime(r.headers['Date'][-24:-4], "%d %b %Y %H:%M:%S").timetuple()))
    return st - lt


def count_waiting_time(time_to_wait, time_template, api_version, entity=''):
    diff = get_time_difference(api_version, entity)
    wait_to = int(time.mktime(datetime.strptime(time_to_wait, time_template).timetuple()))
    time_now = int(time.mktime(datetime.now().timetuple()))
    return (wait_to - diff) - time_now


# get list of qualifications for tender (SQLA)
def list_of_qualifications(tender_id_long, api_version):
    print('Get list of qualifications')
    tender_json = TenderRequests(api_version).get_tender_info(tender_id_long)
    response = tender_json.json()
    qualifications = response['data']['qualifications']
    return qualifications


# select my bids
def pass_pre_qualification(qualifications, tender_id_long, tender_token, api_version):
    list_of_my_bids = BidsTender.query.filter_by(tender_id=tender_id_long).all()
    my_bids = []
    tender = TenderRequests(api_version)
    for x in range(len(list_of_my_bids)):  # select bid_id of every bid
        my_bids.append(list_of_my_bids[x].bid_id)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        qualification_bid_id = qualifications[x]['bidID']
        if qualification_bid_id in my_bids:
            time.sleep(1)
            add_document_to_entity(tender_id_long, qualification_id, tender_token, api_version, 'qualifications')
            tender.approve_prequalification(tender_id_long, qualification_id, tender_token, prequalification_approve_bid_json)
        else:
            time.sleep(1)
            add_document_to_entity(tender_id_long, qualification_id, tender_token, api_version, 'qualifications', False)
            tender.approve_prequalification(tender_id_long, qualification_id, tender_token, json_status('unsuccessful'))


def pass_second_pre_qualification(qualifications, tender_id, tender_token, api_version):
    tender = TenderRequests(api_version)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        time.sleep(1)
        add_document_to_entity(tender_id, qualification_id, tender_token, api_version, 'qualifications')
        tender.approve_prequalification(tender_id, qualification_id, tender_token, prequalification_approve_bid_json)


def run_activate_award(api_version, tender_id_long, tender_token, list_of_awards, procurement_method):
    tender = TenderRequests(api_version)
    award_number = 0
    activate_award_json = activate_award_limited_json(procurement_method)
    for award in range(len(list_of_awards)):
        award_number += 1
        award_id = list_of_awards[award]['id']
        add_document_to_entity(tender_id_long, award_id, tender_token, api_version, 'awards')
        tender.activate_award_contract(tender_id_long, 'awards', award_id, tender_token, activate_award_json, award_number)


def run_activate_contract(api_version, tender_id_long, tender_token, list_of_contracts, complaint_end_date):
    tender = TenderRequests(api_version)
    contract_number = 0
    json_activate_contract = activate_contract_json(complaint_end_date)
    for contract in range(len(list_of_contracts)):
        contract_number += 1
        contract_id = list_of_contracts[contract]['id']
        add_document_to_entity(tender_id_long, contract_id, tender_token, api_version, 'contracts')
        tender.activate_award_contract(tender_id_long, 'contracts', contract_id, tender_token, json_activate_contract, contract_number)


def save_documents_for_report(request, report_id_long):
    if len(list(request.files.keys())) > 0:
        for f in range(len(list(request.files.keys()))):
            file_key = list(request.files.keys())[f]  # file_key like 'file'
            uploaded_file = request.files[file_key]
            if uploaded_file.filename != '':
                filename = request.files[file_key].filename
                local_filename = get_random_32()  # Generate id_long for document (local_filename == id_long)
                if filename.split('.')[-1] == 'gz' and filename.split('.')[-2] == 'tar':
                    file_extension = 'tar.gz'
                else:
                    file_extension = filename.split('.')[-1]
                # a = uploaded_file.stream.read()  # convert document to bytes
                file_path = os.path.join(REPORTS_DOCS_DIR, '{0}.{1}'.format(local_filename, file_extension))
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                uploaded_file.save(file_path)
                add_document_to_db = ReportDocuments(None, local_filename, '{0}.{1}'.format(local_filename, file_extension), filename, report_id_long)
                db.session.add(add_document_to_db)
                db.session.commit()
                db.session.remove()


def add_new_report(request, session):
    report_title = request.form['reportTitle']
    report_type_id = int(request.form['reportType'])
    report_content = request.form['reportContent']
    report_priority = int(request.form['reportPriority'])
    report_id_long = get_random_32()  # Generate id_long for report
    add_report = Reports(None, report_id_long, report_title, report_type_id, report_content, None, session['user_id'], report_priority, 1)
    db.session.add(add_report)
    db.session.commit()
    db.session.remove()
    save_documents_for_report(request, report_id_long)
    return True


def save_edited_report(request, report_data):
    report_title = request.form['reportTitle']
    report_type_id = int(request.form['reportType'])
    report_content = request.form['reportContent']
    report_priority = int(request.form['reportPriority'])
    report_status = int(request.form['reportStatus'])
    Reports.query.filter_by(id=report_data.id).update(dict(title=report_title, type_id=report_type_id, content=report_content, priority_id=report_priority, status_id=report_status))
    db.session.commit()
    db.session.remove()
    save_documents_for_report(request, report_data.id_long)
    return True
