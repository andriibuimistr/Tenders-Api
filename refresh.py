# -*- coding: utf-8 -*-
from variables import Companies, Tenders, db, host, api_version, Bids
import requests
from datetime import datetime
from flask import abort

tender_byustudio_host = 'http://tender.byustudio.in.ua'
invalid_tender_status_list = ['unsuccessful', 'cancelled']


# update tender status in database (SQLA)
def update_tender_status(tender_status_in_db, tender_id_long, procurement_method_type):
    get_tender_info = requests.get('{}/api/{}/tenders/{}'.format(host, api_version, tender_id_long))
    actual_tender_status = get_tender_info.json()['data']['status']
    if actual_tender_status == tender_status_in_db and actual_tender_status not in invalid_tender_status_list:
        print '{}{}{}{}{}'.format(tender_id_long, ' status is up to date. Status: ', actual_tender_status, ' - ',
                                  procurement_method_type)
        return 0
    else:
        if actual_tender_status in invalid_tender_status_list:
            Bids.query.filter_by(tender_id=tender_id_long).delete()
            db.session.commit()
            delete_unsuccessful_tender = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
            db.session.delete(delete_unsuccessful_tender)
            db.session.commit()
            print '{}{}{}'.format('Tender ', tender_id_long,
                                  ' and its related bids were deleted because of its status')
            return 0
        else:
            Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(tender_status=actual_tender_status))
            db.session.commit()
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

    r = requests.get("{}/api/{}/tenders?mode=test&offset={}-{}-{}T{}%3A{}%3A{}.0%2B03%3A00&limit=1000".format(
        host, api_version, year, month, day, hours, minutes, seconds))
    print "{}/api/{}/tenders?mode=test&offset={}-{}-{}T{}%3A{}%3A{}.0%2B03%3A00&limit=1000".format(
        host, api_version, year, month, day, hours, minutes, seconds)
    updated_tenders = r.json()['data']
    list_of_updated_tenders = []
    for x in range(len(updated_tenders)):
        list_of_updated_tenders.append(updated_tenders[x]['id'])

    cron = open('cron/synchronization.txt', 'w')
    cron.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cron.close()

    try:
        tenders_list = Tenders.query.all()
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
            return 0, n_updated_tenders
    except Exception, e:
        db.session.rollback()
        print e
        return 1, e


# get list of all tenders (SQLA)
def get_tenders_list():
    tenders_list = Tenders.query.all()
    list_of_tenders = []
    if len(tenders_list) == 0:
        print 'Tenders table is empty'
        return {"description": "DB is empty"}
    else:
        print "Get tenders in local DB"
        for tender in range(len(tenders_list)):
            tender_id = tenders_list[tender].tender_id_long
            db_tender_status = tenders_list[tender].tender_status
            procurement_method_type = tenders_list[tender].procurementMethodType
            added_to_site = tenders_list[tender].added_to_site
            if added_to_site == 1:
                added_to_site = True
            else:
                added_to_site = False
            list_of_tenders.append({"tender id": tender_id, "tender status": db_tender_status,
                                    "procurementMethodType": procurement_method_type, 'has company': added_to_site})
        return list_of_tenders


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
                Tenders.query.filter_by(tender_id_long=tender_id_long).update(dict(added_to_site=1,
                                                                                   company_uid=company_uid))
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


# add one tender to company (SQLA)
def add_one_tender_to_company(company_id, company_platform_host, tender_id_long, company_uid):
    get_tender_data = Tenders.query.filter_by(tender_id_long=tender_id_long).first()
    tender_id_long = get_tender_data.tender_id_long
    tender_token = get_tender_data.tender_token
    added_to_site = get_tender_data.added_to_site
    if added_to_site == 0 or added_to_site is None:
        add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
            company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token,
            '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
        add_to_site_response = add_to_site.json()
        if 'tid' in add_to_site_response:
            Tenders.query.filter_by(tender_id_long=tender_id_long).update(
                dict(added_to_site=1, company_uid=company_uid))  # set added to site=1
            db.session.commit()
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
            print 'Tender has company'
            return abort(422, 'Tender has company')
        else:
            print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
            return {'status': 'error', 'description': add_to_site_response}
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
        companies_list.append(
            {"id": int(all_companies[company].id), "company_email": all_companies[company].company_email,
             "company_id": int(all_companies[company].company_id),
             "company_role_id": int(all_companies[company].company_role_id),
             "platform_id": int(all_companies[company].platform_id),
             "company_identifier": all_companies[company].company_identifier})
    return companies_list


# ################################### BIDS ############################
# add one bid to company (SQLA)
def add_one_bid_to_company(company_id, company_platform_host, bid_id, company_uid):
    get_bid_data = Bids.query.filter_by(bid_id=bid_id).first()
    bid_id = get_bid_data.bid_id
    bid_token = get_bid_data.bid_token
    added_to_site = get_bid_data.added_to_site
    tender_id = get_bid_data.tender_id
    if added_to_site == 0 or added_to_site is None:
        add_to_site = requests.get('{}{}{}{}{}{}{}{}{}{}'.format(
            company_platform_host, '/tender/add-bid-to-company?tid=', tender_id, '&bid=', bid_id, '&token=', bid_token,
            '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
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
