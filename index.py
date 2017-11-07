# -*- coding: utf-8 -*-
import variables
import tender
import document
import bid
import json
import sys
import qualification


# procurement_method = 'aboveThresholdUA'
# number_of_lots = 0
# number_of_items = 2
add_documents = 0
# number_of_bids = 1


def create_tender_function():

    procurement_method = variables.procurement_method_selector()
    if procurement_method in variables.above_threshold_procurement:
        number_of_lots = variables.number_of_lots()
        if number_of_lots == 0:
            number_of_items = variables.number_of_items()
        else:
            number_of_items = 0
    elif procurement_method in variables.below_threshold_procurement:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    else:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    number_of_bids = bid.number_of_bids()

    list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)  # get list of id for lots
    # select type of tender (with or without lots)
    if number_of_lots == 0:
        json_tender = json.loads(tender.tender(number_of_lots, number_of_items, procurement_method))
    else:
        json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                         procurement_method))
    headers_tender = tender.headers_tender(json_tender)  # get headers for publish tender
    publish_tender_response = tender.publish_tender(headers_tender, json_tender)  # publish tender in draft status
    activate_tender = tender.activating_tender(publish_tender_response, headers_tender)  # activate tender

    tender_id_long = publish_tender_response.headers['Location'].split('/')[-1]
    tender_token = publish_tender_response.json()['access']['token']
    tender_status = activate_tender.json()['data']['status']

    # add documents to tender
    if add_documents == 1:
        document.add_documents_to_tender(tender_id_long, tender_token)
    # add tender to database
    tender.tender_to_db(tender_id_long, publish_tender_response, tender_token, procurement_method, tender_status,
                        number_of_lots)
    # tender.add_tender_to_site(tender_id_long, tender_token)
    # bids
    bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method, list_of_id_lots)
# create_tender_function()


# ########################## APPROVE PREQUALIFICATION ###################################
def pass_prequalification():
    tender_id_long = raw_input('Tender ID: ')
    tender_token = qualification.get_tender_token(tender_id_long)  # get tender token
    qualifications = qualification.list_of_qualifications(tender_id_long)  # get list of qualifications for tender
    qualification.approve_my_bids(qualifications, tender_id_long, tender_token)  # approve all my bids
    qualification.finish_prequalification(tender_id_long, tender_token)  # submit prequalification protocol
pass_prequalification()
