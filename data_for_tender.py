# -*- coding: utf-8 -*-
from faker import Faker
import json
import random
import os
import binascii
from datetime import datetime, timedelta
import key
import pytz


# ########################################### VARIABLES ############################
fake = Faker('uk_UA')


def host_selector(api_version):
    if api_version == 'dev':
        host = 'https://api-sandbox.prozorro.openprocurement.net'
        api_version = "dev"
        ds_host = 'https://upload.docs-sandbox.prozorro.openprocurement.net/upload'
        host_headers = 'api-sandbox.prozorro.openprocurement.net'
    else:
        host = 'https://lb.api-sandbox.openprocurement.org'
        api_version = "2.4"
        ds_host = 'https://upload.docs-sandbox.openprocurement.org/upload'
        host_headers = 'lb.api-sandbox.openprocurement.org'
    return host, api_version, ds_host, host_headers


sandbox = 1
if sandbox == 2:
    ds_host = 'https://upload.docs-sandbox.prozorro.openprocurement.net/upload'
    host = 'https://api-sandbox.prozorro.openprocurement.net'
    api_version = 'dev'
else:
    ds_host = 'https://upload.docs-sandbox.openprocurement.org/upload'
    host = 'https://lb.api-sandbox.openprocurement.org'
    api_version = '2.4'

auth_key = key.auth_key


tender_currency = random.choice(['UAH', 'USD', 'EUR', 'RUB'])  # 'GBP'
valueAddedTaxIncluded = str(random.choice([True, False])).lower()


# SELECT PROCUREMENT METHOD ############################################################################################################################
above_threshold_procurement = ['aboveThresholdUA', 'aboveThresholdEU', 'aboveThresholdUA.defense', 'competitiveDialogueUA', 'competitiveDialogueEU', 'esco']
below_threshold_procurement = ['belowThreshold']
limited_procurement = ['reporting', 'negotiation', 'negotiation.quick']
list_of_procurement_types = above_threshold_procurement + below_threshold_procurement + limited_procurement  # list of all procurement types - 1st stage only

without_pre_qualification_procedures = ['aboveThresholdUA', 'aboveThresholdUA.defense']
prequalification_procedures = ['aboveThresholdEU', 'esco']
competitive_procedures = ['competitiveDialogueUA', 'competitiveDialogueEU']

competitive_procedures_first_stage = ['competitiveDialogueUA', 'competitiveDialogueEU']
competitive_procedures_second_stage = ['competitiveDialogueUA.stage2', 'competitiveDialogueEU.stage2']

negotiation_procurement = ['negotiation', 'negotiation.quick']
# list of status
tender_status_list = ['active.tendering', 'active.tendering.stage2', 'active.pre-qualification', 'active.pre-qualification.stage2', 'active.qualification', 'complete', 'active.enquiries', 'active', 'active.award',
                      'active.contract']

without_pre_qualification_procedures_status = ['active.tendering', 'active.qualification']
prequalification_procedures_status = ['active.pre-qualification']
competitive_procedures_status = ['active.tendering.stage2', 'complete']
competitive_dialogue_eu_status = ['active.pre-qualification.stage2']
below_threshold_status = ['active.enquiries', 'active.tendering', 'active.qualification']
limited_status = ['active', 'active.award', 'active.contract', 'complete']

statuses_with_high_acceleration = ['active.tendering', 'complete', 'active.enquiries', 'active', 'active.award', 'active.contract']
statuses_negotiation_with_high_acceleration = ['active', 'active.award']
#################################################################################################################################################################


# PLATFORMS AND DATA FOR TENDER CREATION ##################################################################################
platforms = ['http://tender.byustudio.in.ua', 'http://tender-dev.byustudio.in.ua', 'https://tenders.all.biz']
list_of_api_versions = ['2.4', 'dev']

kiev_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


# ITEMS
# generate item description
def description_of_item(di_number_of_lots, di_number_of_items, item_number):
    description_text = u'"Предмет закупки '
    description_item = []
    if di_number_of_lots == 0:
        items_count = 0
        for item in range(di_number_of_items):
            items_count += 1
            item_description = u"{}{}{}{}{}{}".format('"description": ', description_text, items_count, ' - ', fake.text(200).replace('\n', ' '), '"')
            description_item.append(item_description)
        return description_item
    else:
        items_count = 0
        for item in range(di_number_of_lots):
            items_count += 1
            item_description = u"{}{}{}{}{}{}{}{}".format(', "description": ', description_text, item_number, u' Лот ', items_count, ' - ', fake.text(200).replace('\n', ' '), '"')
            description_item.append(item_description)
        return description_item


# generate delivery address
def delivery_address_block():
    delivery_address_json = {"postalCode": "00000",
                             "countryName": "Україна",
                             "streetAddress": "Улица",
                             "region": "Дніпропетровська область",
                             "locality": "Город"
                             }
    delivery_address = u"{}{}".format(
        ', "deliveryAddress": ', json.dumps(delivery_address_json))
    return delivery_address


# generate delivery start date
def delivery_start_date():
    date_week = datetime.now() + timedelta(days=7)
    return date_week.strftime('%Y-%m-%dT%H:%M:%S+03:00')


# generate delivery end date
def delivery_end_date():
    date_month = datetime.now() + timedelta(days=120)
    return date_month.strftime('%Y-%m-%dT%H:%M:%S+03:00')


# generate id for item(s)
def item_id_generator():
    item_id_generated = "{}{}{}".format(', "id": "', (binascii.hexlify(os.urandom(16))), '"')
    return item_id_generated


# generate unit
def unit():
    unit_code = random.choice([['"BX"', u'"ящик"'], ['"D64"', u'"блок"'], ['"E48"', u'"послуга"']])
    unit_fragment = u"{}{}{}{}{}{}{}".format(', "unit": {"code": ', unit_code[0], ', "name": ', unit_code[1], ' }, "quantity": "', random.randint(1, 99999), '"')
    return unit_fragment


# delivery date
delivery_date_data = {"startDate": delivery_start_date(), "endDate": delivery_end_date()}
deliveryDate = u"{}{}".format(', "deliveryDate": ', json.dumps(delivery_date_data))
additionalClassifications = ', "additionalClassifications": [ ]'


# generate data for item
def item_data(id_number_of_lots, id_number_of_items, i, procurement_method, item_number):
    if procurement_method == 'esco':
        data_for_item = u'{}{}{}{}{}{}{}'.format(description_of_item(id_number_of_lots, id_number_of_items, item_number)[i], classification, additionalClassifications, description_en(),
                                                 delivery_address_block(), deliveryDate, item_id_generator())
    else:
        data_for_item = u'{}{}{}{}{}{}{}{}'.format(
            description_of_item(id_number_of_lots, id_number_of_items, item_number)[i], classification, additionalClassifications, description_en(), delivery_address_block(), deliveryDate, item_id_generator(),
            unit())

    return data_for_item


# --LOTS-- ###############

# generate id for lot(s)
def lot_id_generator():
    lot_id_generated = (binascii.hexlify(os.urandom(16)))
    return lot_id_generated


def title_for_lot(lot_number):
    lot_title_en = ', "title_en": "Title of lot in English"'
    lot_random_title = u"{}{}".format(u'Лот ', lot_number)
    lot_title = u"{}{}{}{}{}".format(', "title": ',  '"', lot_random_title, '"', lot_title_en)
    lot_description_en = ', "description_en": "Description of lot in English"'
    lot_description_name = u"{}{}{}{}{}".format(u'"Описание лота ', lot_random_title, ' - ', fake.text(200).replace('\n', ' '), '"')
    lot_description_fragment = u"{}{}{}".format(', "description": ', lot_description_name, lot_description_en)
    lot_data = u'{}{}'.format(lot_title, lot_description_fragment)
    return lot_data


# lot value amount
def lot_values():
    lot_value_amount = random.randint(1000, 100000)
    lot_value = u"{}{}{}".format(', "value": {"amount": "', lot_value_amount, '"}')
    # lot minimal step amount
    minimal_step_amount = '{0:.2f}'.format(lot_value_amount * 0.01)
    minimal_step_fragment = u"{}{}{}".format(', "minimalStep": {"amount": "', minimal_step_amount, '"}')
    # lot guarantee amount
    lot_guarantee_amount = '{0:.2f}'.format(lot_value_amount * 0.02)
    lot_guarantee = u"{}{}{}".format(', "guarantee": {"amount": "', lot_guarantee_amount, '"}')
    values_of_lot = '{}{}{}'.format(lot_value, lot_guarantee, minimal_step_fragment)
    return values_of_lot, lot_value_amount


lot_values = lot_values()


def lot_values_esco():
    minimal_step_percentage = '"minimalStepPercentage": 0.02'
    lot_value_esco = '{}{}'.format(', ', minimal_step_percentage)
    return lot_value_esco


lot_values_esco = lot_values_esco()


# TENDERS
# tender values
def tender_values(tv_number_of_lots, procurement_method):
    if tv_number_of_lots == 0:
        tender_value_amount = lot_values[1]
    else:
        tender_value_amount = lot_values[1] * tv_number_of_lots
    value_json = {"valueAddedTaxIncluded": valueAddedTaxIncluded,
                  "amount": tender_value_amount,
                  "currency": tender_currency
                  }
    tender_value = u"{}{}".format('"value": ', json.dumps(value_json))
    guarantee_json = {"amount": 0,
                      "currency": tender_currency
                      }
    tender_guarantee = u"{}{}".format(', "guarantee": ', json.dumps(guarantee_json))
    tender_minimal_step_json = {"amount": '{0:.2f}'.format(lot_values[1] * 0.01),
                                "currency": tender_currency,
                                "valueAddedTaxIncluded": valueAddedTaxIncluded
                                }
    tender_minimal_step = u"{}{}".format(', "minimalStep": ', json.dumps(tender_minimal_step_json))
    if procurement_method in limited_procurement:
        values_of_tender = '{}'.format(tender_value)
    else:
        values_of_tender = '{}{}{}'.format(tender_value, tender_guarantee, tender_minimal_step)
    return values_of_tender


#######################################################################################################################
def tender_values_esco(tv_number_of_lots):
    funding_kind = '"fundingKind": "other"'
    nbu_discount_rate = '"NBUdiscountRate": 0.99'
    minimal_step_percentage = '"minimalStepPercentage": 0.02'
    esco_values = '{}, {}, {}'.format(funding_kind, nbu_discount_rate, minimal_step_percentage)
    if tv_number_of_lots != 0:
        esco_values = '{}, {}'.format(nbu_discount_rate, minimal_step_percentage)
    return esco_values


# tender classification from list
def classification():
    classification_scheme = u'"scheme": "ДК021", '
    classification_codes = random.choice([[
        '"03000000-1"', u'"Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та супутня продукція"'],
         ['"09000000-3"', u'"Нафтопродукти, паливо, електроенергія та інші джерела енергії"'],
         ['"14000000-1"', u'"Гірнича продукція, неблагородні метали та супутня продукція"']])
    classification_id = u"{}{}{}{}".format(
        '"description": ', classification_codes[1], ', "id": ', classification_codes[0])
    classification_block = u"{}{}{}{}".format(', "classification": {', classification_scheme, classification_id, " }")
    return classification_block


classification = classification()


# random tender description from list
def description_en():
    description_en_text = ['"Description 1"', '"Description 2"', '"Description 3"']
    description_en_fragment = u"{}{}".format(', "description_en": ', random.choice(description_en_text))
    return description_en_fragment


# Generate tender period
def tender_period(accelerator, procurement_method, received_tender_status):
    # tender_start_date
    tender_start_date = datetime.now().strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
    # tender_end_date
    date_day = datetime.now() + timedelta(minutes=int(round(31 * (1440.0 / accelerator)) + 1))
    tender_end_date = date_day.strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
    tender_period_data = u"{}{}{}{}{}{}".format(', "tenderPeriod": {', '"startDate": ', tender_start_date, ', "endDate": ', tender_end_date, '}')

    if procurement_method == 'belowThreshold':
        one_day = datetime.now() + timedelta(minutes=int(round(1 * (1440.0 / accelerator))), seconds=10)
        six_days = datetime.now() + timedelta(minutes=int(round(6 * (1440.0 / accelerator))), seconds=10)
        five_dozens_days = datetime.now() + timedelta(minutes=int(round(60 * (1440.0 / accelerator))), seconds=10)
        tender_start_date = one_day.strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
        tender_end_date = five_dozens_days.strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
        # if received_tender_status == 'active.tendering':
        if received_tender_status == 'active.qualification':
            tender_end_date = six_days.strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
        tender_period_data = u"{}{}{}{}{}{}{}".format(', "tenderPeriod": {"startDate": ', tender_start_date, ', "endDate": ', tender_end_date, '}, "enquiryPeriod": { "endDate": ', tender_start_date, '}')
    return tender_period_data


def tender_titles():
    tender_random_title = u"{}{}".format(u'Тест ', datetime.now().strftime('%d-%H%M%S"'))
    tender_title = u'{}{}"'.format(', "title": "', fake.text(100)).replace('\n', ' ')  # ', "title": "', tender_random_title
    tender_description = u"{}{}{}".format(', "description": ', u'"Примечания для тендера ', tender_random_title)
    tender_title_en = u"{}{}".format(', "title_en": ', '"Title of tender in english"')
    tender_description_en = u"{}{}".format(', "description_en": ', '""')
    tender_title_description = u'{}{}{}{}'.format(tender_title, tender_description, tender_title_en,
                                                  tender_description_en)
    return tender_title_description


def features(procurement_method):
    if procurement_method in limited_procurement:
        tender_features = ''
    else:
        tender_features = u"{}{}".format(', "features": ', '[ ]')
    return tender_features


def procuring_entity():
    procuring_entity_json = {"name": "Тестовая организация ООО Тест",
                             "name_en": "Company name en english",
                             "address": {
                                   "countryName": "Україна",
                                   "region": "місто Київ",
                                   "locality": "Київ",
                                   "streetAddress": "Улица Койкого",
                                   "postalCode": "12345"
                             },
                             "contactPoint": {
                                   "name": fake.name(),
                                   "email": "testik@gmail.test",
                                   "telephone": "+380002222222",
                                   "url": "http://www.site.site",
                                   "name_en": "Name of person in english"
                             },
                             "identifier": {
                                   "id": "00000000",
                                   "scheme": "UA-EDR",
                                   "legalName": "Тестовая организация ООО Тест",
                                   "legalName_en": fake.company()
                             },
                             "kind": "defense"
                             }
    procuring_entity_block = u"{}{}".format(
        ', "procuringEntity": ', json.dumps(procuring_entity_json))
    return procuring_entity_block


def tender_data(procurement_method, accelerator, received_tender_status):
    procurement_method_type = ', "procurementMethodType": "{}"'.format(procurement_method)
    mode = ', "mode": "test"'
    if procurement_method == 'esco':
        submission_method_details = ', "submissionMethodDetails": "quick(mode:no-auction)"'
    else:
        submission_method_details = ', "submissionMethodDetails": "quick(mode:fast-forward)"'
    procurement_method_details = ', "procurementMethodDetails": "quick, accelerator={}"'.format(accelerator)
    status = ', "status": "draft"'
    limited_cause = u', "cause": "noCompetition", "causeDescription": "Створення закупівлі для переговорної процедури за нагальною потребою"'
    if procurement_method in limited_procurement:
        if procurement_method == 'reporting':
            constant_tender_data = u'{}{}{}{}{}'.format(procuring_entity(), procurement_method_type, mode, procurement_method_details, status)
        else:
            constant_tender_data = u'{}{}{}{}{}{}'.format(procuring_entity(), procurement_method_type, mode, procurement_method_details, status, limited_cause)
    else:
        constant_tender_data = u'{}{}{}{}{}{}{}'.format(tender_period(accelerator, procurement_method, received_tender_status), procuring_entity(), procurement_method_type, mode, submission_method_details,
                                                        procurement_method_details, status)
    return constant_tender_data


# VARIABLES FOR BID
# Above threshold procedures with active bid status
above_threshold_active_bid_procurements = ['aboveThresholdUA', 'aboveThresholdUA.defense']

# DOCS
documents_above_procedures = ['aboveThresholdEU', 'esco', 'aboveThresholdUA.defense', 'competitiveDialogueEU.stage2',
                              'aboveThresholdUA', 'competitiveDialogueUA.stage2']
documents_above_non_financial = ['aboveThresholdUA.defense', 'aboveThresholdUA', 'competitiveDialogueUA.stage2']
documents_above_non_confidential = ['aboveThresholdUA.defense', 'aboveThresholdUA', 'competitiveDialogueUA.stage2']

# index.py data
create_tender_required_fields = ['procurementMethodType', 'number_of_lots', 'number_of_items', 'number_of_bids', 'accelerator', 'company_id', 'platform_host', 'api_version', 'tenderStatus']


# Contracts
def activate_contract_json(complaint_end_date):
    contract_end_date = datetime.now() + timedelta(days=120)
    contract_json = {
                      "data": {
                        "period": {
                          "startDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f{}".format(kiev_now)),
                          "endDate": contract_end_date.strftime("%Y-%m-%dT%H:%M:%S.%f{}".format(kiev_now))
                        },
                        "dateSigned": (complaint_end_date + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S.%f{}".format(kiev_now)),
                        "status": "active",
                        "contractNumber": "N1234567890"
                      }
                    }
    return contract_json
