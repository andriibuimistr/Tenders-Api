# -*- coding: utf-8 -*-
from database import db, Companies, Tenders, BidsTender, Platforms, PlatformRoles, Roles, Users, Auctions
import requests
from datetime import datetime
from flask import abort
import time
import sys
from requests.exceptions import ConnectionError
from tenders.tender_requests import TenderRequests


invalid_tender_status_list = ['unsuccessful', 'cancelled']


def time_counter(waiting_time, message):
    for remaining in range(waiting_time, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining to {}.".format(remaining, message))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rOk!\n")


# update tender status in database (SQLA)
# def update_tender_status(tender_status_in_db, tender_id_long, procurement_method_type):
#     get_t_info = requests.get('{}/api/{}/tenders/{}'.format(host, api_version, tender_id_long))
#     actual_tender_status = get_t_info.json()['data']['status']
#     if actual_tender_status == tender_status_in_db and actual_tender_status not in invalid_tender_status_list:
#         print '{}{}{}{}{}'.format(tender_id_long, ' status is up to date. Status: ', actual_tender_status, ' - ',
#                                   procurement_method_type)
#         return 0
#     else:
#         if actual_tender_status in invalid_tender_status_list:
#             BidsTender.query.filter_by(tender_id=tender_id_long).delete()
#             db.session.commit()
#             db.session.close()
#             delete_unsuccessful_tender = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
#             db.session.delete(delete_unsuccessful_tender)
#             db.session.commit()
#             db.session.close()
#             print '{}{}{}'.format('Tender ', tender_id_long,
#                                   ' and its related bids were deleted because of its status')
#             return 0
#         else:
#             Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(tender_status=actual_tender_status))
#             db.session.commit()
#             db.session.close()
#             print '{}{}{}{}{}{}{}'.format(
#                 tender_id_long, ' status was updated from ', tender_status_in_db, ' to ', actual_tender_status, ' - ',
#                 procurement_method_type)
#             return 1
#
#
# # get updated tenders from CDB (SQLA)
# def update_tenders_list():
#     cron = open('cron/synchronization.txt', 'r')
#     last_cron = cron.read()
#     year = last_cron[:4]
#     month = last_cron[5:7]
#     day = last_cron[8:10]
#     hours = last_cron[11:13]
#     minutes = int(last_cron[14:16]) - 1
#     if minutes == 0:
#         minutes = 1
#     seconds = last_cron[17:]
#     cron.close()
#
#     r = requests.get("{}/api/{}/tenders?mode=test&offset={}-{}-{}T{}%3A{}%3A{}.0%2B03%3A00&limit=1000".format(host, api_version, year, month, day, hours, minutes - 1, seconds))
#     updated_tenders = r.json()['data']
#     list_of_updated_tenders = []
#     for x in range(len(updated_tenders)):
#         list_of_updated_tenders.append(updated_tenders[x]['id'])
#
#     try:
#         tenders_list = Tenders.query.all()
#         db.session.close()
#         if len(tenders_list) == 0:
#             print 'DB is empty'
#         else:
#             count = 0
#             print "Update tenders in local DB"
#             n_updated_tenders = 0
#             for tender in range(len(tenders_list)):
#                 tender_id = tenders_list[tender].tender_id_long
#                 db_tender_status = tenders_list[tender].tender_status
#                 procurement_method_type = tenders_list[tender].procurementMethodType
#                 if tender_id in list_of_updated_tenders:
#                     count += 1
#                     num_updated_tenders = update_tender_status(db_tender_status, tender_id, procurement_method_type)
#                     n_updated_tenders += num_updated_tenders
#             print n_updated_tenders
#             print '{}{}'.format(count, ' tenders were found in synchronization list')
#
#             cron = open('cron/synchronization.txt', 'w')
#             cron.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#             cron.close()
#             return 0, n_updated_tenders
#     except Exception, e:
#         db.session.rollback()
#         print e
#         return 1, e


# add one tender company (SQLA) ##############################################
def add_one_tender_company(company_id, company_platform_host, tender_id_long, entity):
    if entity == 'tender':
        get_tender_data = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
        db.session.remove()
        tender_id_long = get_tender_data.tender_id_long
        tender_token = get_tender_data.tender_token
        added_to_site = get_tender_data.added_to_site
    else:
        get_tender_data = Auctions.query.filter_by(auction_id_long=tender_id_long).first()
        db.session.remove()
        tender_id_long = get_tender_data.auction_id_long
        tender_token = get_tender_data.auction_token
        added_to_site = get_tender_data.added_to_site

    if added_to_site == 0 or added_to_site is None:
        response = None
        add_count = 1
        for x in range(30):
            print "Adding {} to company. Attempt {}".format(entity, add_count)
            try:
                add_count += 1
                add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token, '&company=', company_id,
                                                                     '&acc_token=SUPPPER_SEEECRET_STRIIING'))
                add_to_site_response = add_to_site.json()
                if type(add_to_site_response) == int and entity == 'auction':
                    Auctions.query.filter_by(auction_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    print '\nAuction was added to site - ' + tender_id_long
                    link_to_tender = '{}{}'.format(company_platform_host, '/buyer/tender/view/')
                    response = {'status': 'success'}, 201, link_to_tender
                    break
                if 'tid' in add_to_site_response:
                    Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    db.session.commit()
                    db.session.remove()
                    print '\nTender was added to site - ' + tender_id_long
                    tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                    link_to_tender_print = '{}{}{}{}'.format('Link: ', company_platform_host, '/buyer/tender/view/', add_to_site_response['tid'])
                    link_to_tender = '{}{}{}'.format(company_platform_host, '/buyer/tender/view/', add_to_site_response['tid'])
                    print tender_id_site
                    print link_to_tender_print
                    response = {'status': 'success'}, 201, link_to_tender
                    break
                elif 'tender has company' in add_to_site_response['error']:
                    if entity == 'tender':
                        Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    elif entity == 'auction':
                        Auctions.query.filter_by(auction_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    print 'Tender has company'
                    response = {'status': 'error', 'description': 'Tender has company'}, 422
                    break
                else:
                    print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
                    response = {'status': 'error', 'description': add_to_site_response}, 422
                    time.sleep(20)
                    continue
            except ConnectionError as e:
                print 'Connection Error'
                if add_count < 31:
                    time.sleep(1)
                    continue
                else:
                    abort(500, 'Publish auction error: ' + str(e))
            except requests.exceptions.MissingSchema as e:
                abort(500, 'Publish auction error: ' + str(e))
            except Exception as e:
                if add_count < 31:
                    time.sleep(1)
                    continue
                else:
                    abort(500, 'Publish auction error: ' + str(e))
        return response
    else:
        print '{} {}{}'.format(entity, tender_id_long, ' was added to company before')
        return abort(422, '{} was added to site before'.format(entity))


# list of tenders in prequalification status (SQLA)
def get_tenders_prequalification_status():
    list_tenders_preq = Tenders.query.filter_by(tender_status='active.pre-qualification').all()
    list_json = []
    for x in range(len(list_tenders_preq)):
        id_tp = list_tenders_preq[x].tender_id_long
        procedure = list_tenders_preq[x].procurementMethodType
        status = list_tenders_preq[x].tender_status
        list_json.append({"id": id_tp, "procurementMethodType": procedure, "status": status})
    return {'data': {"tenders": list_json}}


# get list of companies (SQLA)
def get_list_of_companies():
    all_companies = Companies.query.all()
    companies_list = []
    for company in range(len(all_companies)):
        company_type = Roles.query.filter_by(id=all_companies[company].company_role_id).first().role_name
        company_platform_name = Platforms.query.filter_by(id=all_companies[company].platform_id).first().platform_name
        companies_list.append(
            {"id": int(all_companies[company].id), "company_email": all_companies[company].company_email,
             "company_id": int(all_companies[company].company_id),
             "company_role_id": int(all_companies[company].company_role_id),
             "company_role": company_type,
             "platform_id": int(all_companies[company].platform_id),
             "company_identifier": all_companies[company].company_identifier,
             "platform_name": company_platform_name}
        )
    db.session.remove()
    return companies_list


# ################################### BIDS ############################
# add one bid to company (SQLA)
def add_one_bid_to_company(company_platform_host, company_id, bid_id):
    get_bid_data = BidsTender.query.filter_by(bid_id=bid_id).first()
    bid_id = get_bid_data.bid_id
    bid_token = get_bid_data.bid_token
    added_to_site = get_bid_data.added_to_site
    tender_id = get_bid_data.tender_id
    db.session.commit()
    if added_to_site == 0 or added_to_site is None:
        add_to_site = requests.get('{}{}{}{}{}{}{}{}{}{}'.format(
            company_platform_host, '/tender/add-bid-to-company?tid=', tender_id, '&bid=', bid_id, '&token=', bid_token, '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
        add_to_site_response = add_to_site.json()
        print add_to_site_response
        if 'tid' in add_to_site_response and add_to_site.status_code == 200:
            BidsTender.query.filter_by(bid_id=bid_id).update(
                dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
            db.session.commit()
            print '\nBid was added to company - ' + bid_id
            bid_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
            print bid_id_site
            return {'status': 'success'}, 201
        elif 'Bid exist' in add_to_site_response['error']:
            BidsTender.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1))  # set added to site=1
            db.session.commit()
            print 'Bid has company'
            return abort(422, 'Bid has company')
        else:
            print '{}{}{}'.format(bid_id, ' - ', add_to_site_response)
            return {'status': 'error', 'description': add_to_site_response}
    else:
        print '{}{}{}'.format('Bid ', bid_id, ' was added to company before')
        return abort(422, 'Bid was added to company before')


# get list of platform (SQLA)
def get_list_of_platforms(platform_role):
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


# get list of users
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


def get_list_of_tenders():
    tenders_list = Tenders.query.order_by("id desc").all()  # from last to first
    db.session.remove()
    return tenders_list


def check_if_contract_exists(get_t_info):
    try:
        if get_t_info.json()['data']['contracts']:
            return 200
    except Exception as e:
        print e
        return e


def get_time_difference(api_version):
    lt = int(time.mktime(datetime.utcnow().timetuple()))
    r = TenderRequests(api_version).get_list_of_tenders()
    st = int(time.mktime(datetime.strptime(r.headers['Date'][-24:-4], "%d %b %Y %H:%M:%S").timetuple()))
    return st - lt


def count_waiting_time(time_to_wait, time_template, api_version):
    diff = get_time_difference(api_version)
    wait_to = int(time.mktime(datetime.strptime(time_to_wait, time_template).timetuple()))
    time_now = int(time.mktime(datetime.now().timetuple()))
    return (wait_to - diff) - time_now
