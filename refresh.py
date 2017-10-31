# -*- coding: utf-8 -*-
import MySQLdb
import requests


tender_byustudio_host = 'http://tender.byustudio.in.ua'


host = "https://lb.api-sandbox.openprocurement.org/api/2.3/tenders/"
db = MySQLdb.connect(host="82.163.176.242", user="carrosde_python", passwd="python", db="carrosde_tenders")
# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
cursor = db.cursor()

list_of_tenders = "SELECT tender_id_long, tender_status FROM tenders"
cursor.execute(list_of_tenders)

tenders_list = cursor.fetchall()


def get_tender_status(tender_status_in_db, tender_id_long):
    get_tender_info = requests.get(host + tender_id_long)
    actual_tender_status = get_tender_info.json()['data']['status']
    if actual_tender_status == tender_status_in_db and actual_tender_status != 'unsuccessful':
        print '{}{}{}'.format(tender_id_long, ' status is up to date. Status: ', actual_tender_status)
    else:
        if actual_tender_status == 'unsuccessful':
            delete_unsuccessful_tender = 'DELETE FROM tenders WHERE tender_id_long = "{}"'.format(tender_id_long)
            delete_unsuccessful_bids = \
                'DELETE FROM bids WHERE tender_id = "{}"'.format(tender_id_long)
            cursor.execute(delete_unsuccessful_bids)
            cursor.execute(delete_unsuccessful_tender)
            print '{}{}{}'.format('Tender ', tender_id_long,
                                  ' and its related bids were deleted because of "unsuccessful" status')
        else:
            update_tender_status = \
                'UPDATE tenders SET tender_status = "{}" WHERE tender_id_long = "{}"'.format(
                    actual_tender_status, tender_id_long)
            cursor.execute(update_tender_status)
            print '{}{}{}{}{}'.format(
                tender_id_long, ' status was updated from ', tender_status_in_db, ' to ', actual_tender_status)

if len(tenders_list) == 0:
    print 'DB is empty'

for tender in range(len(tenders_list)):
    tender_id = tenders_list[tender][0]
    db_tender_status = tenders_list[tender][1]
    get_tender_status(db_tender_status, tender_id)


def add_tender_to_site():
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
                mark_as_added = 'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added)
                print 'Tender was added to site - ' + tender_id_long
                tender_id_site = '{}{}'.format('Tender ID is: ', add_to_site_response['tid'])
                link_to_tender = '{}{}{}{}'.format(
                    'Link: ', tender_byustudio_host, '/buyer/tender/view/', add_to_site_response['tid'])
                print tender_id_site
                print link_to_tender
            elif 'tender has company' in add_to_site_response['error']:
                mark_as_added_before = 'UPDATE tenders SET added_to_site = 1 WHERE tender_id_long = "{}"'.format(tender_id_long)
                cursor.execute(mark_as_added_before)
                print 'Tender has company'
            else:
                print '{}{}{}'.format(tender_id_long, ' - ', add_to_site_response)
        else:
            print '{}{}{}'.format('Tender ', tender_id_long, ' was added to site before', )
add_tender_to_site()


db.commit()
db.close()
