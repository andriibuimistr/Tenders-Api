# -*- coding: utf-8 -*-
from tenders.data_for_tender import *
from tenders.data_for_monitoring import *
from document import *
from pprint import pprint

cdb = '2.4'
procurement_method = 'belowThreshold'
json_tender = generate_tender_json(procurement_method, number_of_lots=0, number_of_items=3, accelerator=1, received_tender_status='active.tendering', list_of_lots_id=[], if_features=0, skip_auction=True)
tender = TenderRequests(cdb)
t_publish = tender.publish_tender(json_tender)

tender_id_long = t_publish.json()['data']['id']
tender_token = t_publish.json()['access']['token']

time.sleep(1)
t_activate = tender.activate_tender(tender_id_long, tender_token, procurement_method)
print(t_activate.json()['data']['tenderID'])


def document():
    return add_document_to_tender_ds(cdb)


json_monitoring = generate_monitoring_json(tender_id_long, accelerator=1440)
monitoring = Monitoring(cdb)
mn = monitoring.publish_monitoring(json_monitoring)
monitoring_id = mn.json()['data']['id']

add_decision = monitoring.patch_monitoring(monitoring_id, generate_decision(cdb, True), 'Add decision to monitoring')
a_monitoring = monitoring.patch_monitoring(monitoring_id, json_status_active, 'Activate monitoring')


monitoring_owner_token = monitoring.get_monitoring_token(monitoring_id, tender_token).json()['access']['token']

add_post = monitoring.add_post(monitoring_id, generate_json_for_post(document()))

add_conclusion = monitoring.patch_monitoring(monitoring_id, generate_conclusion_true(document()), 'Add conclusion to monitoring')
monitoring_to_addressed = monitoring.patch_monitoring(monitoring_id, json_status_addressed, 'Monitoring to addressed status')
# pprint(monitoring_to_addressed.json())

add_elimination_report = monitoring.add_elimination_report(monitoring_id, monitoring_owner_token, elimination_report(document()))
add_elimination_resolution = monitoring.patch_monitoring(monitoring_id, elimination_resolution(document()), 'Add eliminationResolution to monitoring')
pprint(add_elimination_resolution.json())
