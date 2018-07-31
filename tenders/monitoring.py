# -*- coding: utf-8 -*-
from tenders.data_for_tender import *
from tenders.data_for_monitoring import *
from pprint import pprint
from core import *
from tenders.tender import tender_to_db
import core


def document(api_version):
    return add_document_to_tender_ds(api_version)


def creation_of_monitoring(data, user_id):
    procurement_method = data["procurementMethodType"]
    monitoring_accelerator = int(data["accelerator"])
    company_id = int(data['company_id'])
    platform_host = data['platform_host']
    api_version = data['api_version']
    received_monitoring_status = data['monitoringStatus']
    print(data)

    add_documents_monitoring = 0
    if 'docs_for_monitoring' in data:
        add_documents_monitoring = 1

    json_tender = generate_tender_json(procurement_method, number_of_lots=0, number_of_items=3, accelerator=1, received_tender_status='active.tendering', list_of_lots_id=[], if_features=0, skip_auction=True)
    tender = TenderRequests(api_version)
    t_publish = tender.publish_tender(json_tender)

    tender_id_long = t_publish.json()['data']['id']
    tender_token = t_publish.json()['access']['token']
    tender_id_short = t_publish.json()['data']['tenderID']

    time.sleep(1)
    t_activate = tender.activate_tender(tender_id_long, tender_token, procurement_method)
    print(t_activate.json()['data']['tenderID'])
    tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, 'active.tendering', 0, user_id, api_version)
    core.add_one_tender_company(company_id, platform_host, tender_id_long, tender_token, 'tender')

    json_monitoring = generate_monitoring_json(tender_id_long, accelerator=monitoring_accelerator)
    monitoring = Monitoring(api_version)
    mn = monitoring.publish_monitoring(json_monitoring)
    monitoring_id = mn.json()['data']['id']

    add_decision = monitoring.patch_monitoring(monitoring_id, generate_decision(api_version, add_documents_monitoring), 'Add decision to monitoring')
    a_monitoring = monitoring.patch_monitoring(monitoring_id, json_status_active, 'Activate monitoring')

    monitoring_owner_token = monitoring.get_monitoring_token(monitoring_id, tender_token).json()['access']['token']

    add_post = monitoring.add_post(monitoring_id, generate_json_for_post(document(api_version)))

    add_conclusion = monitoring.patch_monitoring(monitoring_id, generate_conclusion_true(document(api_version)), 'Add conclusion to monitoring')
    monitoring_to_addressed = monitoring.patch_monitoring(monitoring_id, json_status_addressed, 'Monitoring to addressed status')

    add_elimination_report = monitoring.add_elimination_report(monitoring_id, monitoring_owner_token, elimination_report(document(api_version)))
    add_elimination_resolution = monitoring.patch_monitoring(monitoring_id, elimination_resolution(document(api_version)), 'Add eliminationResolution to monitoring')

    elimination_period = monitoring.get_monitoring_info(monitoring_id).json()['data']['eliminationPeriod']['endDate']
    waiting_time = count_waiting_time(elimination_period, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_now), api_version, 'monitoring')
    time_counter(waiting_time, 'Wait for eliminationPeriod endDate')
    monitoring_to_completed = monitoring.patch_monitoring(monitoring_id, json_status_completed, 'Change monitoring status to completed')
    pprint(monitoring_to_completed.json())
    return 1, 1
