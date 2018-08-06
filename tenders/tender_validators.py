# -*- coding: utf-8 -*-
from tender_additional_data import *
from flask import abort
import core
from database import BidsTender, Tenders, db
from language.translations import alert


def validator_create_tender(data):
    for field in range(len(create_tender_required_fields)):
        if create_tender_required_fields[field] not in data:
            abort(400, "Field '{}' is required. List of required fields: {}".format(create_tender_required_fields[field], create_tender_required_fields))

    procurement_method = data["procurementMethodType"]
    number_of_items = data["number_of_items"]
    accelerator = data["accelerator"]
    company_id = data['company_id']
    received_tender_status = data['tenderStatus']
    api_version = data['api_version']
    platform_host = data['platform_host']

    if 'number_of_lots' in data and len(data["number_of_lots"]) > 0:
        number_of_lots = data["number_of_lots"]
        if str(number_of_lots).isdigit() is False:
            abort(400, 'Number of lots must be integer')
        elif 0 > int(number_of_lots) or int(number_of_lots) > 20:
            abort(422, 'Number of lots must be between 0 and 20')

    if str(number_of_items).isdigit() is False:
        abort(400, 'Number of items must be integer')
    elif 1 > int(number_of_items) or int(number_of_items) > 20:
        abort(422, 'Number of items must be between 1 and 20')

    if procurement_method not in limited_procurement:
        if "number_of_bids" in data:
            number_of_bids = data["number_of_bids"]
            if str(number_of_bids).isdigit() is True:
                if 0 > int(number_of_bids) or int(number_of_bids) > 10:
                    abort(422, 'Number of bids must be between 0 and 10')
            if str(number_of_bids).isdigit() is False and len(number_of_bids) > 0:
                abort(400, 'Number of bids must be integer')

    if str(accelerator).isdigit() is False:
        abort(400, 'Accelerator must be integer')
    elif 1 > int(accelerator) or int(accelerator) > 30000:
        abort(422, 'Accelerator must be between 1 and 30000')

    if procurement_method == 'belowThreshold':
        if int(accelerator) > 14400:
            abort(422, 'For belowThreshold accelerator value can\'t be greater than 14400')
        if received_tender_status == 'active.qualification':
            if int(accelerator) > 1440:
                abort(422, 'For belowThreshold procedure in "active.qualification" accelerator value can\'t be greater than 1440')

    if str(company_id).isdigit() is False:
        abort(400, 'Company ID must be integer')
    if int(company_id) == 0:
        abort(422, 'Company id can\'t be 0')

    if received_tender_status not in tender_status_list:
        return abort(422, 'Tender status must be one of: {}'.format(tender_status_list))
    if api_version not in list_of_api_versions:
        return abort(422, 'API version must be one of: {}'.format(list_of_api_versions))
    if platform_host not in core.get_list_of_platform_urls(1):
        return abort(422, 'Platform must be one of: {}'.format(core.get_list_of_platform_urls(1)))

    if procurement_method not in limited_procurement:
        if 'skip_auction' not in data and received_tender_status not in ['active.tendering', 'active.pre-qualification', 'active.enquiries', 'complete']:
            abort(422, '"skip_auction" must be checked for {} status'.format(received_tender_status))

    # check procurement method
    if procurement_method in above_threshold_procurement:  # check allowed statuses for above threshold procurements
        # check status for procedure
        if procurement_method in without_pre_qualification_procedures:
            if received_tender_status not in without_pre_qualification_procedures_status:
                return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status))
        elif procurement_method in prequalification_procedures:
            if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status:
                return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status))
        elif procurement_method in competitive_procedures:
            if procurement_method == 'competitiveDialogueUA':
                if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status:
                    return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status))
            else:
                if received_tender_status not in without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status + competitive_dialogue_eu_status:
                    return abort(422, "For '{}' status must be one of: {}".format(procurement_method, without_pre_qualification_procedures_status + prequalification_procedures_status + competitive_procedures_status +
                                                                                  competitive_dialogue_eu_status))
    elif procurement_method in below_threshold_procurement:  # check allowed status for below threshold procedure
        if received_tender_status not in below_threshold_status:
            abort(422, "For '{}' status must be one of: {}".format(procurement_method, below_threshold_status))
    elif procurement_method in limited_procurement:  # check allowed status for limited procedures
        if received_tender_status not in limited_status:
            abort(422, "For '{}' status must be one of: {}".format(procurement_method, limited_status))
    else:  # incorrect procurementMethodType
        abort(422, 'procurementMethodType must be one of: {}'.format(above_threshold_procurement + below_threshold_procurement + limited_procurement))

    if int(accelerator) < 30:
        if received_tender_status not in statuses_with_high_acceleration:
            abort(422, 'Accelerator value can be less than 30 for the following statuses only: {}'.format(statuses_with_high_acceleration))
        if procurement_method in negotiation_procurement and received_tender_status not in statuses_negotiation_with_high_acceleration:
            abort(422, 'Accelerator value can be less than 30 for: {} for the following statuses only: {}'.format(negotiation_procurement, statuses_negotiation_with_high_acceleration))
        if procurement_method == 'belowThreshold' and received_tender_status != 'active.enquiries':
            abort(422, 'For {} accelerator value can be less than 30 for the following status only: {}'.format('"belowThreshold"', 'active.enquiries'))


def validator_create_monitoring(data):
    for field in range(len(create_monitoring_required_fields)):
        if create_monitoring_required_fields[field] not in data:
            abort(400, "Field '{}' is required. List of required fields: {}".format(create_monitoring_required_fields[field], create_monitoring_required_fields))

    if data['monitoringStatus'] in monitoring_status_list_with_high_acceleration and int(data['accelerator']) < 1440:
        abort(422, 'Accelerator can\'t be less than 1440 for "{}" status'.format(data['monitoringStatus']))


def validator_add_tender_bid_to_company(bid_id, data):
    list_of_bids = BidsTender.query.all()
    list_bid = []
    for tid in range(len(list_of_bids)):
        list_bid.append(list_of_bids[tid].bid_id)
    if bid_id not in list_bid:
        abort(404, 'Bid id was not found in database')

    if 'company-id' not in data:
        abort(400, 'Company UID was not found in request')

    if str(data['company-id']).isdigit() is False:
        abort(400, 'Company UID must be integer')

    if int(data['company-id']) == 0:
        abort(422, 'Company id can\'t be 0')

    return data


def validator_if_tender_id_short_in_db(tender_id_short):
    list_of_tenders = Tenders.query.all()
    list_tid = []
    for tid in range(len(list_of_tenders)):
        db.session.remove()
        list_tid.append(list_of_tenders[tid].tender_id_short)
    if tender_id_short not in list_tid:
        abort(404, alert.error_404_not_found('alert_error_404_no_tender_id'))
    return True
