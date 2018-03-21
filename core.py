# -*- coding: utf-8 -*-
from database import db, Tenders, BidsTender, Platforms, PlatformRoles, Roles, Users, Auctions, BidsAuction
import requests
from datetime import datetime
from flask import abort
import time
import sys
from requests.exceptions import ConnectionError

from tenders.data_for_tender import activate_contract_json
from tenders.tender_additional_data import prequalification_approve_bid_json, prequalification_decline_bid_json
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
            print "Adding {} to company. Attempt {}".format(entity, add_count)
            try:
                add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(company_platform_host, '/tender/add-tender-to-company?tid=', entity_id_long, '&token=', entity_token, '&company=', company_id,
                                                                     '&acc_token=SUPPPER_SEEECRET_STRIIING'))
                add_to_site_response = add_to_site.json()
                if type(add_to_site_response) == int and entity == 'auction':
                    Auctions.query.filter_by(auction_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    print '\nAuction was added to site - ' + entity_id_long
                    response = {'status': 'success'}, 201
                    break
                if 'tid' in add_to_site_response:
                    Tenders.query.filter_by(tender_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    db.session.commit()
                    db.session.remove()
                    print '\nTender was added to site - ' + entity_id_long
                    response = {'status': 'success'}, 201
                    break
                elif 'tender has company' in add_to_site_response['error']:
                    if entity == 'tender':
                        Tenders.query.filter_by(tender_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                    elif entity == 'auction':
                        Auctions.query.filter_by(auction_id_long=entity_id_long).update(dict(added_to_site=1, company_uid=company_id))
                    db.session.commit()
                    db.session.remove()
                    print '{} has company'.format(entity)
                    response = {'status': 'error'}, 422
                    break
                else:
                    print '{}{}{}'.format(entity_id_long, ' - ', add_to_site_response)
                    response = {'status': 'error'}, 422
                    time.sleep(20)
                    continue
            except ConnectionError as e:
                print 'Connection Error'
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
                    abort(500, 'Publish {} error: ' + str(e))
        return response
    else:
        print '{} {}{}'.format(entity, entity_id_long, ' was added to company before')
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
    db.session.commit()

    if added_to_site == 0 or added_to_site is None:
        add_count = 0
        for x in range(30):
            add_count += 1
            print "Adding bid to company. Attempt {}".format(add_count)
            try:
                add_to_site = requests.get('{}{}{}{}{}{}{}{}{}{}'.format(
                    company_platform_host, '/tender/add-bid-to-company?tid=', tender_id, '&bid=', bid_id, '&token=', bid_token, '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
                add_to_site_response = add_to_site.json()
                print add_to_site_response
                if 'tid' in add_to_site_response and add_to_site.status_code == 200:
                    if entity == 'tender':
                        BidsTender.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    else:
                        BidsAuction.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1, company_id=company_id, bid_platform=company_platform_host))  # set added to site=1
                    db.session.commit()
                    print '\nBid was added to company - ' + bid_id
                    print '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                    return {'status': 'success'}, 201
                elif 'Bid exist' in add_to_site_response['error']:
                    if entity == 'tender':
                        BidsTender.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1))  # set added to site=1
                    else:
                        BidsAuction.query.filter_by(bid_id=bid_id).update(dict(added_to_site=1))  # set added to site=1
                    db.session.commit()
                    print 'Bid has company'
                    abort(422, 'Bid has company')
                else:
                    print '{}{}{}'.format(bid_id, ' - ', add_to_site_response)
                    return {'status': 'error', 'description': add_to_site_response}
            except Exception as e:
                if add_count < 30:
                    time.sleep(1)
                    continue
                else:
                    abort(500, 'Publish {} error: ' + str(e))
    else:
        print '{}{}{}'.format('Bid ', bid_id, ' was added to company before')
        abort(422, 'Bid was added to company before')


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


def activate_award_json_select(procurement_method):
    if procurement_method == 'reporting':
        activate_award_json_negotiation = {
            "data": {
                "status": "active"
            }
        }
    else:
        activate_award_json_negotiation = {
                                  "data": {
                                    "status": "active",
                                    "qualified": True
                                  }
                                }
    return activate_award_json_negotiation


# get list of qualifications for tender (SQLA)
def list_of_qualifications(tender_id_long, api_version):
    print 'Get list of qualifications'
    tender_json = TenderRequests(api_version).get_tender_info(tender_id_long)
    response = tender_json.json()
    qualifications = response['data']['qualifications']
    return qualifications


# select my bids
def pass_pre_qualification(qualifications, tender_id_long, tender_token, api_version):
    list_of_my_bids = BidsTender.query.filter_by(tender_id=tender_id_long).all()
    my_bids = []
    bids_json = []
    tender = TenderRequests(api_version)
    for x in range(len(list_of_my_bids)):  # select bid_id of every bid
        my_bids.append(list_of_my_bids[x].bid_id)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        qualification_bid_id = qualifications[x]['bidID']
        if qualification_bid_id in my_bids:
            time.sleep(1)
            action = tender.approve_prequalification(tender_id_long, qualification_id, tender_token, prequalification_approve_bid_json)
        else:
            time.sleep(1)
            action = tender.approve_prequalification(tender_id_long, qualification_id, tender_token, prequalification_decline_bid_json)
        bids_json.append(action)
    return bids_json


def pass_second_pre_qualification(qualifications, tender_id, tender_token, api_version):
    bids_json = []
    tender = TenderRequests(api_version)
    for x in range(len(qualifications)):
        qualification_id = qualifications[x]['id']
        time.sleep(1)
        action = tender.approve_prequalification(tender_id, qualification_id, tender_token, prequalification_approve_bid_json)
        bids_json.append(action)
    return bids_json


def run_activate_award(api_version, tender_id_long, tender_token, list_of_awards, procurement_method):
    tender = TenderRequests(api_version)
    award_number = 0
    activate_award_json = activate_award_json_select(procurement_method)
    for award in range(len(list_of_awards)):
        award_number += 1
        award_id = list_of_awards[award]['id']
        tender.activate_award_contract(tender_id_long, 'awards', award_id, tender_token, activate_award_json, award_number)


def run_activate_contract(api_version, tender_id_long, tender_token, list_of_contracts, complaint_end_date):
    tender = TenderRequests(api_version)
    contract_number = 0
    json_activate_contract = activate_contract_json(complaint_end_date)
    for contract in range(len(list_of_contracts)):
        contract_number += 1
        contract_id = list_of_contracts[contract]['id']
        tender.activate_award_contract(tender_id_long, 'contracts', contract_id, tender_token, json_activate_contract, contract_number)
