# -*- coding: utf-8 -*-
from tenders.data_for_tender import *
from tenders.data_for_monitoring import *
from core import *
from tenders.tender import tender_to_db
import core


def wait_for_elimination_period_end_date(monitoring, monitoring_id_long, api_version):
    elimination_period = monitoring.get_monitoring_info(monitoring_id_long).json()['data']['eliminationPeriod']['endDate']
    waiting_time = count_waiting_time(elimination_period, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_now), api_version, 'monitoring')
    time_counter(waiting_time, 'Wait for eliminationPeriod endDate')


def creation_of_monitoring(data, user_id):
    procurement_method = data["procurementMethodType"]
    monitoring_accelerator = int(data["accelerator"])
    company_id = int(data['company_id'])
    platform_host = data['platform_host']
    api_version = data['api_version']
    received_monitoring_status = data['monitoringStatus']

    add_documents_monitoring = False
    if 'docs_for_monitoring' in data:
        add_documents_monitoring = True

    response_json = dict()
    tender = TenderRequests(api_version)
    if 'tender_id_long' in data and len(data['tender_id_long']) > 0:
        if received_monitoring_status == 'completed':
            abort(422, 'Can\'t create monitoring in "completed" status for existent tender')
        tender_id_long = data['tender_id_long']
        get_t_info = tender.get_tender_info(tender_id_long)
        tender_token = None
        tender_id_short = get_t_info.json()['data']['tenderID']
        response_json['tender_to_company'] = '', '#'
    else:
        json_tender = generate_tender_json(procurement_method, number_of_lots=0, number_of_items=3,
                                           accelerator=1, received_tender_status='active.tendering',
                                           list_of_lots_id=[], if_features=0, skip_auction=True)
        t_publish = tender.publish_tender(json_tender)
        tender_id_long = t_publish.json()['data']['id']
        tender_token = t_publish.json()['access']['token']
        tender_id_short = t_publish.json()['data']['tenderID']
        time.sleep(1)
        tender.activate_tender(tender_id_long, tender_token, procurement_method)
        print(tender_id_short)
        tender_to_db(tender_id_long, tender_id_short, tender_token, procurement_method, 'active.tendering', 0, user_id, api_version)
        add_tender_company = core.add_one_tender_company(company_id, platform_host, tender_id_long, tender_token, 'tender')
        response_json['tender_to_company'] = add_tender_company[0], '{}{}{}'.format(platform_host, '/buyer/tender/view/', add_tender_company[2])

    response_json['id'] = tender_id_short
    response_code = 201
    response_json['status'] = 'success'
    response_json['monitoringStatus'] = 'MONITORING INITIAL STATUS'

    json_monitoring = generate_monitoring_json(tender_id_long, accelerator=monitoring_accelerator)
    monitoring = Monitoring(api_version)
    mn = monitoring.publish_monitoring(json_monitoring)
    monitoring_id_long = mn.json()['data']['id']

    if received_monitoring_status == 'cancelled':
        monitoring.patch_monitoring(monitoring_id_long, monitoring_to_cancelled_json(), 'Monitoring to cancelled status')  # Change monitoring status to "cancelled"
        get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
        if get_m_info.json()['data']['status'] == 'cancelled':
            response_json['monitoringStatus'] = get_m_info.json()['data']['status']
            return response_json, response_code
        else:
            abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

    monitoring.patch_monitoring(monitoring_id_long, generate_decision(api_version, add_documents_monitoring), 'Add decision to monitoring')  # Add decision to monitoring in "draft" status
    monitoring.patch_monitoring(monitoring_id_long, json_status_active, 'Activate monitoring')  # Activate monitoring

    if received_monitoring_status == 'active.stopped':
        monitoring.patch_monitoring(monitoring_id_long, monitoring_to_stopped_json(), 'Monitoring to stopped status')  # Change monitoring status from "active" to "stopped"
        get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
        if get_m_info.json()['data']['status'] == 'stopped':
            response_json['monitoringStatus'] = get_m_info.json()['data']['status']
            return response_json, response_code
        else:
            abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

    if received_monitoring_status == 'active':
        get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
        if get_m_info.json()['data']['status'] == 'active':
            response_json['monitoringStatus'] = get_m_info.json()['data']['status']
            return response_json, response_code
        else:
            abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

    monitoring.add_post(monitoring_id_long, generate_json_for_post(api_version, add_documents_monitoring))  # Add post to monitoring

    if received_monitoring_status in monitoring_status_list_violation_false:  # If received monitoring status is in "monitoring_status_list_violation_false" list
        monitoring.patch_monitoring(monitoring_id_long, generate_conclusion_false(api_version, add_documents_monitoring), 'Add conclusion FALSE to monitoring')  # Add conclusion FALSE to monitoring
        monitoring.patch_monitoring(monitoring_id_long, json_status_declined, 'Monitoring to declined status')  # Change monitoring status to "declined"
        if received_monitoring_status == 'declined':
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'declined':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))
        # If received monitoring status is not "declined"
        if received_monitoring_status == 'closed':
            wait_for_elimination_period_end_date(monitoring, monitoring_id_long, api_version)
            monitoring.patch_monitoring(monitoring_id_long, json_status_closed, 'Monitoring to closed status')  # Change monitoring status to "closed"
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'closed':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

        if received_monitoring_status == 'declined.stopped':
            monitoring.patch_monitoring(monitoring_id_long, monitoring_to_stopped_json(), 'Monitoring to stopped status')  # Change monitoring status from "active" to "stopped"
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'stopped':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))
    else:
        monitoring.patch_monitoring(monitoring_id_long, generate_conclusion_true(api_version, add_documents_monitoring), 'Add conclusion TRUE to monitoring')  # Add conclusion TRUE to monitoring
        monitoring.patch_monitoring(monitoring_id_long, json_status_addressed, 'Monitoring to addressed status')  # Change monitoring status to addressed
        if received_monitoring_status == 'addressed':
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'addressed':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

        if received_monitoring_status == 'addressed.stopped':
            monitoring.patch_monitoring(monitoring_id_long, monitoring_to_stopped_json(), 'Monitoring to stopped status')  # Change monitoring status from "active" to "stopped"
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'stopped':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))

        monitoring_owner_token = monitoring.get_monitoring_token(monitoring_id_long, tender_token).json()['access']['token']
        monitoring.add_elimination_report(monitoring_id_long, monitoring_owner_token, elimination_report(api_version, add_documents_monitoring))  # Add elimination report
        monitoring.patch_monitoring(monitoring_id_long, elimination_resolution(api_version, add_documents_monitoring), 'Add eliminationResolution to monitoring')  # Add add elimination resolution
        wait_for_elimination_period_end_date(monitoring, monitoring_id_long, api_version)
        monitoring.patch_monitoring(monitoring_id_long, json_status_completed, 'Change monitoring status to completed')  # Monitoring to "completed" status
        if received_monitoring_status == 'completed':
            get_m_info = monitoring.get_monitoring_info(monitoring_id_long)
            if get_m_info.json()['data']['status'] == 'completed':
                response_json['monitoringStatus'] = get_m_info.json()['data']['status']
                return response_json, response_code
            else:
                abort(422, 'Monitoring status: '.format(get_m_info.json()['data']['status']))
        return response_json, response_code
