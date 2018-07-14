# -*- coding: utf-8 -*-
from cdb_requests import *
from tenders.data_for_tender import *
from tenders.data_for_monitoring import *

cdb = '2.4'
procurement_method = 'belowThreshold'
json_tender = generate_tender_json(procurement_method, 0, 3, 1, 'active.tendering', [], 0, True)
tender = TenderRequests(cdb)
t_publish = tender.publish_tender(json_tender)

tender_id_long = t_publish.json()['data']['id']
tender_token = t_publish.json()['access']['token']

time.sleep(1)
t_activate = tender.activate_tender(tender_id_long, tender_token, procurement_method)

json_monitoring = generate_monitoring_json(tender_id_long, accelerator=1440)
monitoring = Monitoring(cdb)
mn = monitoring.publish_monitoring(json_monitoring)
monitoring_id = mn.json()['data']['id']

add_decision = monitoring.patch_monitoring(monitoring_id, generate_decision(), 'Add decision to monitoring')
a_monitoring = monitoring.patch_monitoring(monitoring_id, json_status_active, 'Activate monitoring')
# print(a_monitoring.json())

add_post = monitoring.add_post(monitoring_id, generate_json_for_post())

add_conclusion = monitoring.patch_monitoring(monitoring_id, generate_conclusion_true(), 'Add conclusion to monitoring')
monitoring_to_addressed = monitoring.patch_monitoring(monitoring_id, json_status_addressed, 'Monitoring to addressed status')
