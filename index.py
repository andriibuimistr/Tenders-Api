# -*- coding: utf-8 -*-
import variables
import tender
import document
import bid
import json
import sys


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


#procurement_method = 'aboveThresholdUA'
#number_of_lots = 0
#number_of_items = 2
add_documents = 0
#number_of_bids = 1


list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)


if number_of_lots == 0:
    json_tender = json.loads(tender.tender(number_of_lots, number_of_items, procurement_method))
else:
    json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                     procurement_method))

headers_tender = tender.headers_tender(json_tender)

publish_tender_response = tender.publish_tender(headers_tender, json_tender)
activate_tender = tender.activating_tender(publish_tender_response, headers_tender)

tender_id_long = publish_tender_response.headers['Location'].split('/')[-1]
tender_token = publish_tender_response.json()['access']['token']
tender_status = activate_tender.json()['data']['status']
tender_id_short = publish_tender_response.json()['data']['tenderID']


def add_docs():
    if add_documents == 1:
        document.add_documents_to_tender(tender_id_long, tender_token)
add_docs()

add_tender_to_db = tender.tender_to_db(tender_id_long, publish_tender_response, tender_token, procurement_method,
                                       tender_status, number_of_lots)

# add_tender_to_site = tender.add_tender_to_site(tender_id_long, tender_token)

# BIDS

bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method, list_of_id_lots)
