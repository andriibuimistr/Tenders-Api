# -*- coding: utf-8 -*-
import requests


tender_byustudio_host = 'http://tender.byustudio.in.ua'
host = "https://lb.api-sandbox.openprocurement.org/api/2.3/tenders/"

invalid_tender_status_list = ['unsuccessful', 'cancelled']


def update_tender_status(tender_status_in_db, tender_id_long, procurement_method_type, cursor):
    get_tender_info = requests.get(host + tender_id_long)
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


def update_tenders_list(cursor):
    list_of_tenders = "SELECT tender_id_long, tender_status, procurementMethodType FROM tenders"
    cursor.execute(list_of_tenders)
    tenders_list = cursor.fetchall()
    if len(tenders_list) == 0:
        print 'DB is empty'
    else:
        print "Update tenders in local DB"
        for tender in range(len(tenders_list)):
            tender_id = tenders_list[tender][0]
            db_tender_status = tenders_list[tender][1]
            procurement_method_type = tenders_list[tender][2]
            update_tender_status(db_tender_status, tender_id, procurement_method_type, cursor)


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


def add_all_tenders_to_company(cursor):
    print '\nAdd tenders to site'
    actual_list_of_tenders = "SELECT tender_id_long, tender_token, added_to_site FROM tenders"
    cursor.execute(actual_list_of_tenders)
    tenders_actual_list = cursor.fetchall()
    for every_tender in range(len(tenders_actual_list)):
        tender_id_long = tenders_actual_list[every_tender][0]
        tender_token = tenders_actual_list[every_tender][1]
        added_to_site = tenders_actual_list[every_tender][2]
        company_id = 61
        if added_to_site == 0 or added_to_site is None:
            add_to_site = requests.get('{}{}{}{}{}{}{}{}'.format(
                tender_byustudio_host, '/tender/add-tender-to-company?tid=', tender_id_long, '&token=', tender_token,
                '&company=', company_id, '&acc_token=SUPPPER_SEEECRET_STRIIING'))
            add_to_site_response = add_to_site.json()
            if 'tid' in add_to_site_response:
                mark_as_added = \
                    'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added)
                print '\nTender was added to site - ' + tender_id_long
                tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                link_to_tender = '{}{}{}{}'.format(
                    'Link: ', tender_byustudio_host, '/buyer/tender/view/', add_to_site_response['tid'])
                print tender_id_site
                print link_to_tender
            elif 'tender has company' in add_to_site_response['error']:
                mark_as_added_before = \
                    'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added_before)
                print 'Tender has company'
            else:
                print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
        else:
            print '{}{}{}'.format('Tender ', tender_id_long, ' was added to site before', )

# add_tender_to_site()


def get_tenders_prequalification_status(cursor):
    list_tenders_prequalification = "SELECT tender_id_long, procurementMethodType, tender_status FROM tenders WHERE " \
                                    "tender_status = 'active.pre-qualification'"
    cursor.execute(list_tenders_prequalification)
    tenders_prequalification_list = cursor.fetchall()
    return tenders_prequalification_list
