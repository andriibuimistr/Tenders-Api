# -*- coding: utf-8 -*-
from cdb_requests import *
from tenders.data_for_tender import *
from tenders.data_for_monitoring import *

procurement_method = 'belowThreshold'
json_tender = generate_tender_json(procurement_method, 0, 3, 1, 'active.tendering', [], 0, True)
tender = TenderRequests('2.4')
t_publish = tender.publish_tender(json_tender)

tender_id_long = t_publish.json()['data']['id']
tender_token = t_publish.json()['access']['token']

time.sleep(1)
t_activate = tender.activate_tender(tender_id_long, tender_token, procurement_method)

json_monitoring = generate_monitoring_json(tender_id_long)
monitoring = Monitoring()
mn = monitoring.publish_monitoring(json_monitoring)
monitoring_id = mn.json()['data']['id']

add_decision = monitoring.add_decision(monitoring_id, generate_decision())
a_monitoring = monitoring.activate_monitoring(monitoring_id)

