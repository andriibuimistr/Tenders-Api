# -*- coding: utf-8 -*-
import requests
from variables import host, api_version
from datetime import datetime


tender_byustudio_host = 'http://tender.byustudio.in.ua'
invalid_tender_status_list = ['unsuccessful', 'cancelled']


# update tender status in database
def update_tender_status(tender_status_in_db, tender_id_long, procurement_method_type, cursor):
    get_tender_info = requests.get('{}/api/{}/tenders/{}'.format(host, api_version, tender_id_long))
    actual_tender_status = get_tender_info.json()['data']['status']
    if actual_tender_status == tender_status_in_db and actual_tender_status not in invalid_tender_status_list:
        print '{}{}{}{}{}'.format(tender_id_long, ' status is up to date. Status: ', actual_tender_status, ' - ',
                                  procurement_method_type)
    else:
        if actual_tender_status in invalid_tender_status_list:
            delete_unsuccessful_tender = 'DELETE FROM tenders WHERE tender_id_long = "{}"'.format(tender_id_long)
            delete_unsuccessful_bids = \
                'DELETE FROM bids WHERE tender_id = "{}"'.format(tender_id_long)
            cursor.execute(delete_unsuccessful_bids)
            cursor.execute(delete_unsuccessful_tender)
            print '{}{}{}'.format('Tender ', tender_id_long,
                                  ' and its related bids were deleted because of it\'s status')
        else:
            sql_update_tender_status = \
                'UPDATE tenders SET tender_status = "{}" WHERE tender_id_long = "{}"'.format(
                    actual_tender_status, tender_id_long)
            cursor.execute(sql_update_tender_status)
            print '{}{}{}{}{}{}{}'.format(
                tender_id_long, ' status was updated from ', tender_status_in_db, ' to ', actual_tender_status, ' - ',
                procurement_method_type)


# get updated tenders from CDB
def update_tenders_list(cursor):
    cron = open('cron/synchronization.txt', 'r')
    last_cron = cron.read()
    print last_cron
    year = last_cron[:4]
    month = last_cron[5:7]
    day = last_cron[8:10]
    hours = last_cron[11:13]
    minutes = int(last_cron[14:16]) - 1
    seconds = last_cron[17:]
    cron.close()

    r = requests.get("{}/api/{}/tenders?mode=test&offset={}-{}-{}T{}%3A{}%3A{}.0%2B03%3A00".format(
        host, api_version, year, month, day, hours, minutes, seconds))
    updated_tenders = r.json()['data']
    list_of_updated_tenders = []
    for x in range(len(updated_tenders)):
        list_of_updated_tenders.append(updated_tenders[x]['id'])

    cron = open('cron/synchronization.txt', 'w')
    cron.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cron.close()

    list_of_tenders = "SELECT tender_id_long, tender_status, procurementMethodType FROM tenders"
    cursor.execute(list_of_tenders)
    tenders_list = cursor.fetchall()
    if len(tenders_list) == 0:
        print 'DB is empty'
    else:
        count = 0
        print "Update tenders in local DB"
        for tender in range(len(tenders_list)):
            tender_id = tenders_list[tender][0]
            db_tender_status = tenders_list[tender][1]
            procurement_method_type = tenders_list[tender][2]
            if tender_id in list_of_updated_tenders:
                count += 1
                update_tender_status(db_tender_status, tender_id, procurement_method_type, cursor)
        print '{}{}'.format(count, ' tenders were found in synchronization list')


def get_tenders_list(cursor):
    list_of_tenders = "SELECT tender_id_long, tender_status, procurementMethodType FROM tenders"
    cursor.execute(list_of_tenders)
    tenders_list = cursor.fetchall()
    list_of_tenders = []
    if len(tenders_list) == 0:
        print 'DB is empty'
        return {"description": "DB is empty"}
    else:
        print "Get tenders in local DB"
        for tender in range(len(tenders_list)):
            tender_id = tenders_list[tender][0]
            db_tender_status = tenders_list[tender][1]
            procurement_method_type = tenders_list[tender][2]
            list_of_tenders.append({"tender id": tender_id, "tender status": db_tender_status,
                                    "procurementMethodType": procurement_method_type})
        return list_of_tenders


# add all tenders to company
def add_all_tenders_to_company(cursor, company_id, company_platform_host):
    print '\nAdd tenders to site'
    actual_list_of_tenders = "SELECT tender_id_long, tender_token, added_to_site FROM tenders"
    cursor.execute(actual_list_of_tenders)
    tenders_actual_list = cursor.fetchall()
    count = 0
    for every_tender in range(len(tenders_actual_list)):
        tender_id_long = tenders_actual_list[every_tender][0]
        tender_token = tenders_actual_list[every_tender][1]
        added_to_site = tenders_actual_list[every_tender][2]
        if added_to_site == 0 or added_to_site is None:
            add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
                company_platform_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token,
                '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
            add_to_site_response = add_to_site.json()
            if 'tid' in add_to_site_response:
                mark_as_added = \
                    'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added)
                print '\nTender was added to site - ' + tender_id_long
                tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                link_to_tender = '{}{}{}{}'.format(
                    'Link: ', company_platform_host, '/buyer/tender/view/', add_to_site_response['tid'])
                print tender_id_site
                print link_to_tender
                count += 1
            elif 'tender has company' in add_to_site_response['error']:
                mark_as_added_before = \
                    'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added_before)
                print 'Tender has company'
            else:
                print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
        else:
            print '{}{}{}'.format('Tender ', tender_id_long, ' was added to site before', )
    return count


# list of tenders in prequalification status
def get_tenders_prequalification_status(cursor):
    list_tenders_prequalification = "SELECT tender_id_long, procurementMethodType, tender_status FROM tenders WHERE " \
                                    "tender_status = 'active.pre-qualification'"
    cursor.execute(list_tenders_prequalification)
    tenders_prequalification_list = cursor.fetchall()
    return tenders_prequalification_list
