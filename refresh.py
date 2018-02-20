# -*- coding: utf-8 -*-
from variables import Companies, Tenders, db, host, api_version, Bids, Platforms, Roles
import requests
from datetime import datetime
from flask import abort
import time
import sys
from requests.exceptions import ConnectionError


invalid_tender_status_list = ['unsuccessful', 'cancelled']


def time_counter(waiting_time, message):
    for remaining in range(waiting_time, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining to {}.".format(remaining, message))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rOk!\n")


# update tender status in database (SQLA)
def update_tender_status(tender_status_in_db, tender_id_long, procurement_method_type):
    get_t_info = requests.get('{}/api/{}/tenders/{}'.format(host, api_version, tender_id_long))
    actual_tender_status = get_t_info.json()['data']['status']
    if actual_tender_status == tender_status_in_db and actual_tender_status not in invalid_tender_status_list:
        print '{}{}{}{}{}'.format(tender_id_long, ' status is up to date. Status: ', actual_tender_status, ' - ',
                                  procurement_method_type)
        return 0
    else:
        if actual_tender_status in invalid_tender_status_list:
            Bids.query.filter_by(tender_id=tender_id_long).delete()
            db.session.commit()
            db.session.close()
            delete_unsuccessful_tender = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
            db.session.delete(delete_unsuccessful_tender)
            db.session.commit()
            db.session.close()
            print '{}{}{}'.format('Tender ', tender_id_long,
                                  ' and its related bids were deleted because of its status')
            return 0
        else:
            Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(tender_status=actual_tender_status))
            db.session.commit()
            db.session.close()
            print '{}{}{}{}{}{}{}'.format(
                tender_id_long, ' status was updated from ', tender_status_in_db, ' to ', actual_tender_status, ' - ',
                procurement_method_type)
            return 1


# get updated tenders from CDB (SQLA)
def update_tenders_list():
    cron = open('cron/synchronization.txt', 'r')
    last_cron = cron.read()
    year = last_cron[:4]
    month = last_cron[5:7]
    day = last_cron[8:10]
    hours = last_cron[11:13]
    minutes = int(last_cron[14:16]) - 1
    if minutes == 0:
        minutes = 1
    seconds = last_cron[17:]
    cron.close()

    r = requests.get("{}/api/{}/tenders?mode=test&offset={}-{}-{}T{}%3A{}%3A{}.0%2B03%3A00&limit=1000".format(host, api_version, year, month, day, hours, minutes - 1, seconds))
    updated_tenders = r.json()['data']
    list_of_updated_tenders = []
    for x in range(len(updated_tenders)):
        list_of_updated_tenders.append(updated_tenders[x]['id'])

    try:
        tenders_list = Tenders.query.all()
        db.session.close()
        if len(tenders_list) == 0:
            print 'DB is empty'
        else:
            count = 0
            print "Update tenders in local DB"
            n_updated_tenders = 0
            for tender in range(len(tenders_list)):
                tender_id = tenders_list[tender].tender_id_long
                db_tender_status = tenders_list[tender].tender_status
                procurement_method_type = tenders_list[tender].procurementMethodType
                if tender_id in list_of_updated_tenders:
                    count += 1
                    num_updated_tenders = update_tender_status(db_tender_status, tender_id, procurement_method_type)
                    n_updated_tenders += num_updated_tenders
            print n_updated_tenders
            print '{}{}'.format(count, ' tenders were found in synchronization list')

            cron = open('cron/synchronization.txt', 'w')
            cron.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cron.close()
            return 0, n_updated_tenders
    except Exception, e:
        db.session.rollback()
        print e
        return 1, e


# get list of all tenders (SQLA)
def get_tenders_list():
    tenders_list = Tenders.query.all()
    db.session.remove()
    list_of_tenders = []
    if len(tenders_list) == 0:
        print 'Tenders table is empty'
        return 1, {"description": "DB is empty"}
    else:
        print "Get tenders in local DB"
        for tender in range(len(tenders_list)):
            tender_id_long = tenders_list[tender].tender_id_long
            db_tender_status = tenders_list[tender].tender_status
            procurement_method_type = tenders_list[tender].procurementMethodType
            added_to_site = tenders_list[tender].added_to_site
            company_uid = tenders_list[tender].company_uid

            # list_of_tenders.append({"tender_id": tender_id, "tender_status": db_tender_status,
            #                         "procurementMethodType": procurement_method_type})
            if added_to_site == 1:
                # list_of_tenders[tender]['has_company'] = True
                tender_company = company_uid
            else:
                tender_company = 0
            list_of_tenders.append({"id": tender_id_long, "procurement_method_type": procurement_method_type, "tender_status": db_tender_status, "tender_company": tender_company})
        return 0, list_of_tenders


# add all tenders to company (SQLA)
def add_all_tenders_to_company(company_id, company_platform_host, company_uid):
    print '\nAdd tenders to site'
    tenders_actual_list = Tenders.query.all()
    count = 0
    for every_tender in range(len(tenders_actual_list)):
        tender_id_long = tenders_actual_list[every_tender].tender_id_long
        tender_token = tenders_actual_list[every_tender].tender_token
        added_to_site = tenders_actual_list[every_tender].added_to_site
        if added_to_site == 0 or added_to_site is None:
            add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
                company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token,
                '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
            add_to_site_response = add_to_site.json()
            if 'tid' in add_to_site_response:
                Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_uid))
                db.session.commit()
                print '\nTender was added to site - ' + tender_id_long
                tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                link_to_tender = '{}{}{}{}'.format(
                    'Link: ', company_platform_host, 'buyer/tender/view/', add_to_site_response['tid'])
                print tender_id_site
                print link_to_tender
                count += 1
            elif 'tender has company' in add_to_site_response['error']:
                Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1,
                                                                                   company_uid=company_uid))
                db.session.commit()
                print 'Tender has company'
            else:
                print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
        else:
            print '{}{}{}'.format('Tender ', tender_id_long, ' was added to site before', )
    return count


# add one tender company (SQLA) ##############################################
def add_one_tender_company(company_id, company_platform_host, tender_id_long):
    get_tender_data = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
    db.session.remove()
    tender_id_long = get_tender_data.tender_id_long
    tender_token = get_tender_data.tender_token
    added_to_site = get_tender_data.added_to_site
    if added_to_site == 0 or added_to_site is None:
        response = None
        add_count = 1
        for x in range(30):
            print "Adding tender to company. Attempt " + str(add_count)
            add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token, '&company=', company_id,
                                                                 '&acc_token=SUPPPER_SEEECRET_STRIIING'))
            add_to_site_response = add_to_site.json()
            if 'tid' in add_to_site_response:
                Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                db.session.commit()
                db.session.remove()
                print '\nTender was added to site - ' + tender_id_long
                tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                link_to_tender = '{}{}{}{}'.format(
                    'Link: ', company_platform_host, '/buyer/tender/view/', add_to_site_response['tid'])
                print tender_id_site
                print link_to_tender
                response = {'status': 'success'}, 201, link_to_tender
                break
            elif 'tender has company' in add_to_site_response['error']:
                Tenders.query.filter_by(tender_id_long=tender_id_long).update(
                    dict(added_to_site=1, company_uid=company_id))  # set added to site=1
                db.session.commit()
                db.session.remove()
                print 'Tender has company'
                response = {'status': 'error', 'description': 'Tender has company'}, 422
                break
            else:
                print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
                response = {'status': 'error', 'description': add_to_site_response}, 422
                add_count += 1
                time.sleep(20)
                continue
        return response
    else:
        print '{}{}{}'.format('Tender ', tender_id_long, ' was added to company before')
        return abort(422, 'Tender was added to site before')


# add one tender to company (SQLA)
def add_one_tender_to_company(company_id, company_platform_host, tender_id_long, company_uid):
    get_tender_data = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
    db.session.remove()
    tender_id_long = get_tender_data.tender_id_long
    tender_token = get_tender_data.tender_token
    added_to_site = get_tender_data.added_to_site
    if added_to_site == 0 or added_to_site is None:
        add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
            company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token, '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
        add_to_site_response = add_to_site.json()
        if 'tid' in add_to_site_response:
            Tenders.query.filter_by(tender_id_long=tender_id_long).update(
                dict(added_to_site=1, company_uid=company_uid))  # set added to site=1
            db.session.commit()
            db.session.remove()
            print '\nTender was added to site - ' + tender_id_long
            tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
            link_to_tender = '{}{}{}{}'.format(
                'Link: ', company_platform_host, '/buyer/tender/view/', add_to_site_response['tid'])
            print tender_id_site
            print link_to_tender
            return {'status': 'success'}, 201
        elif 'tender has company' in add_to_site_response['error']:
            Tenders.query.filter_by(tender_id_long=tender_id_long).update(
                dict(added_to_site=1, company_uid=company_uid))  # set added to site=1
            db.session.commit()
            db.session.remove()
            print 'Tender has company'
            return {'status': 'error', 'description': 'Tender has company'}, 422
        else:
            print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
            return {'status': 'error', 'description': add_to_site_response}, 422
    else:
        print '{}{}{}'.format('Tender ', tender_id_long, ' was added to company before')
        return abort(422, 'Tender was added to site before')


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
def add_one_bid_to_company(company_id, company_platform_host, bid_id, company_uid):
    get_bid_data = Bids.query.filter_by(bid_id=bid_id).first()
    bid_id = get_bid_data.bid_id
    bid_token = get_bid_data.bid_token
    added_to_site = get_bid_data.added_to_site
    tender_id = get_bid_data.tender_id
    db.session.commit()
    if added_to_site == 0 or added_to_site is None:
        add_to_site = requests.get('{}{}{}{}{}{}{}{}{}{}'.format(
            company_platform_host, '/tender/add-bid-to-company?tid=', tender_id, '&bid=', bid_id, '&token=', bid_token, '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
        add_to_site_response = add_to_site.json()
        if 'tid' in add_to_site_response:
            Bids.query.filter_by(bid_id=bid_id).update(
                dict(added_to_site=1, company_uid=company_uid))  # set added to site=1
            db.session.commit()
            print '\nBid was added to company - ' + bid_id
            bid_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
            print bid_id_site
            return {'status': 'success'}, 201
        elif 'Bid exist' in add_to_site_response['error']:
            Bids.query.filter_by(bid_id=bid_id).update(
                dict(added_to_site=1, company_uid=company_uid))  # set added to site=1
            db.session.commit()
            print 'Bid has company'
            return abort(422, 'Bid has company')
        else:
            print '{}{}{}'.format(bid_id, ' - ', add_to_site_response)
            return {'status': 'error', 'description': add_to_site_response}
    else:
        print '{}{}{}'.format('Bid ', bid_id, ' was added to company before')
        return abort(422, 'Bid was added to company before')


# get list of companies (SQLA)
def get_list_of_platforms():
    all_platforms = Platforms.query.all()
    platforms_list = []
    for platform in range(len(all_platforms)):
        platforms_list.append({"id": int(all_platforms[platform].id), "platform_name": all_platforms[platform].platform_name, "platform_url": all_platforms[platform].platform_url})
    db.session.remove()
    return platforms_list


def check_if_contract_exists(get_t_info):
    try:
        if get_t_info[1].json()['data']['contracts']:
            return 200
    except Exception as e:
        print e
        return e


def get_tender_info(host_kit, tender_id_long):
    attempts = 0
    for x in range(5):
        attempts += 1
        # print 'Get tender info. Attempt {}'.format(attempts)
        try:
            get_t_info = requests.get("{}/api/{}/tenders/{}".format(host_kit[0], host_kit[1], tender_id_long))
            if get_t_info.status_code == 200:
                return get_t_info.status_code, get_t_info
            else:
                print get_t_info.content
                time.sleep(1)
                if attempts >= 5:
                    abort(get_t_info.status_code, get_t_info.content)
        except Exception as e:
            print e
            if attempts < 5:
                time.sleep(1)
                continue
            else:
                abort(500, 'Get tender info error: ' + str(e))


'''def get_tender_info2(host_kit, tender_id_long):
    attempts = 0
    for x in range(5):
        attempts += 1
        print 'Get tender info. Attempt {}'.format(attempts)
        try:
            get_t_info = requests.get("{}/api/{}/tenders/{}".format(host_kit[0], host_kit[1], '111'))
            if get_t_info.status_code == 200:
                return get_t_info.status_code, get_t_info
            else:
                print get_t_info.content
                if attempts < 5:
                    continue
                else:
                    return get_t_info.status_code, get_t_info
        except Exception as e:
            print 'CDB Error'
            if attempts < 5:
                continue
            else:
                print 'Exception. Can\'t get tender info'
                return 500, e'''
