# -*- coding: utf-8 -*-
from faker import Faker
import json
import random
import os
import binascii
from datetime import datetime, timedelta
import key
import pytz
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# ########################################### SQLAlchemy ####################################
app = Flask(__name__)
db_host = '82.163.176.242'
user = 'carrosde_python'
password = 'python'
d_base = 'carrosde_tenders'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(user, password, db_host, d_base)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 90
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 50

db = SQLAlchemy(app)


class Companies(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_email = db.Column(db.String(255))
    company_id = db.Column(db.String(255))
    company_role_id = db.Column(db.String(255))
    platform_id = db.Column(db.String(255))
    company_identifier = db.Column(db.String(255))

    def __init__(self, id, company_email, company_id, company_role_id, platform_id, company_identifier):
        self.id = id
        self.company_email = company_email
        self.company_id = company_id
        self.company_role_id = company_role_id
        self.platform_id = platform_id
        self.company_identifier = company_identifier


class Tenders(db.Model):
    __tablename__ = 'tenders'
    id = db.Column(db.Integer, primary_key=True)
    tender_id_long = db.Column(db.String(255))
    tender_id_short = db.Column(db.String(255))
    tender_token = db.Column(db.String(255))
    procurementMethodType = db.Column(db.String(255))
    related_tender_id = db.Column(db.String(255))
    tender_status = db.Column(db.String(255))
    n_lots = db.Column(db.Integer)
    tender_platform_id = db.Column(db.Integer)
    company_uid = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)

    def __init__(self, id, tender_id_long, tender_id_short, tender_token, procurementMethodType, related_tender_id,
                 tender_status, n_lots, tender_platform_id, company_uid, added_to_site):
        self.id = id
        self.tender_id_long = tender_id_long
        self.tender_id_short = tender_id_short
        self.tender_token = tender_token
        self.procurementMethodType = procurementMethodType
        self.related_tender_id = related_tender_id
        self.tender_status = tender_status
        self.n_lots = n_lots
        self.tender_platform_id = tender_platform_id
        self.company_uid = company_uid
        self.added_to_site = added_to_site


class Bids(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.String(255))
    bid_token = db.Column(db.String(255))
    tender_id = db.Column(db.String(255))
    bid_status = db.Column(db.String(255))
    bid_platform_id = db.Column(db.Integer)
    company_uid = db.Column(db.Integer)
    added_to_site = db.Column(db.Integer)
    user_identifier = db.Column(db.String(255))

    def __init__(self, id, bid_id, bid_token, tender_id, bid_status, bid_platform_id,
                 company_uid, added_to_site, user_identifier):
        self.id = id
        self.bid_id = bid_id
        self.bid_token = bid_token
        self.tender_id = tender_id
        self.bid_status = bid_status
        self.bid_platform_id = bid_platform_id
        self.company_uid = company_uid
        self.added_to_site = added_to_site
        self.user_identifier = user_identifier


class Platforms(db.Model):
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(255))
    platform_url = db.Column(db.String(255))

    def __init__(self, id, platform_name, platform_url):
        self.id = id
        self.platform_name = platform_name
        self.platform_url = platform_url


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255))

    def __init__(self, id, role_name):
        self.id = id
        self.role_name = role_name


# ########################################### GLOBAL VARIABLES ############################
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

sandbox = 2
if sandbox == 2:
    ds_host = 'https://upload.docs-sandbox.prozorro.openprocurement.net/upload'
    host = "https://api-sandbox.prozorro.openprocurement.net"
    api_version = "dev"
else:
    ds_host = 'https://upload.docs-sandbox.openprocurement.org/upload'
    host = "https://lb.api-sandbox.openprocurement.org"
    api_version = "2.4"

auth_key = key.auth_key


tender_currency = random.choice(['UAH', 'USD', 'EUR', 'RUB', 'GBP'])
valueAddedTaxIncluded = str(random.choice([True, False])).lower()


# SELECT PROCUREMENT METHOD
above_threshold_procurement = ['aboveThresholdUA', 'aboveThresholdEU', 'aboveThresholdUA.defense', 'competitiveDialogueUA', 'competitiveDialogueEU', 'esco']
below_threshold_procurement = ['open_belowThreshold']
limited_procurement = ['limited_reporting', 'limited_negotiation', 'limited_negotiation.quick']

prequalification_procedures = ['aboveThresholdEU', 'competitiveDialogueUA', 'competitiveDialogueEU', 'esco', 'competitiveDialogueEU.stage2']

above_procedures_without_pre_qualification = ['aboveThresholdUA', 'aboveThresholdUA.defense']
one_stage_pre_qualification_procedures = ['aboveThresholdEU', 'esco']

tender_status_list = ['active.tendering', 'active.tendering.stage2', 'active.pre-qualification', 'active.pre-qualification.stage2', 'active.qualification', 'complete']
competitive_procedures = ['competitiveDialogueUA', 'competitiveDialogueEU', 'competitiveDialogueUA.stage2', 'competitiveDialogueEU.stage2']
competitive_procedures_first_stage = ['competitiveDialogueUA', 'competitiveDialogueEU']
competitive_procedures_second_stage = ['competitiveDialogueUA.stage2', 'competitiveDialogueEU.stage2']


# ITEMS
# generate item description
def description_of_item(di_number_of_lots, di_number_of_items):
    description_text = u'"Описание предмета закупки '
    description_item = []
    if di_number_of_lots == 0:
        items_count = 0
        for item in range(di_number_of_items):
            items_count += 1
            item_description = u"{}{}{}{}".format('"description": ', description_text, items_count, '"')
            description_item.append(item_description)
        return description_item
    else:
        items_count = 0
        for item in range(di_number_of_lots):
            items_count += 1
            item_description = u"{}{}{}{}{}".format(', "description": ', description_text,
                                                    u'Лот ', items_count, '"')
            description_item.append(item_description)
        return description_item


# generate delivery address
def delivery_address_block():
    delivery_address_json = {"postalCode": fake.postcode(),
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
    unit_fragment = u"{}{}{}{}{}{}{}".format(', "unit": {"code": ', unit_code[0], ', "name": ', unit_code[1],
                                             ' }, "quantity": "', random.randint(1, 99999), '"')
    return unit_fragment


# delivery date
delivery_date_data = {"startDate": delivery_start_date(), "endDate": delivery_end_date()}
deliveryDate = u"{}{}".format(', "deliveryDate": ', json.dumps(delivery_date_data))
additionalClassifications = ', "additionalClassifications": [ ]'


# generate data for item
def item_data(id_number_of_lots, id_number_of_items, i, procurement_method):
    if procurement_method == 'esco':
        data_for_item = u'{}{}{}{}{}{}{}'.format(
            description_of_item(id_number_of_lots, id_number_of_items)[i], classification, additionalClassifications,
            description_en(), delivery_address_block(),
            deliveryDate, item_id_generator())
    else:
        data_for_item = u'{}{}{}{}{}{}{}{}'.format(
            description_of_item(id_number_of_lots, id_number_of_items)[i], classification, additionalClassifications,
            description_en(), delivery_address_block(),
            deliveryDate, item_id_generator(), unit())

    return data_for_item


# --LOTS-- ###############

# generate id for lot(s)
def lot_id_generator():
    lot_id_generated = (binascii.hexlify(os.urandom(16)))
    return lot_id_generated


def title_for_lot():
    lot_title_en = ', "title_en": ""'
    lot_random_title = u"{}{}".format(u'Лот ', random.randint(1, 99999))
    lot_title = u"{}{}{}{}{}".format(', "title": ',  '"', lot_random_title, '"', lot_title_en)
    lot_description_en = ', "description_en": ""'
    lot_description_name = u"{}{}{}".format(u'"Описание лота ', lot_random_title, '"')
    lot_description_fragment = u"{}{}{}".format(', "description": ', lot_description_name, lot_description_en)
    lot_data = u'{}{}'.format(lot_title, lot_description_fragment)
    return lot_data


# lot value amount
def lot_values():
    lot_value_amount = random.randint(1000, 100000)
    lot_value = u"{}{}{}".format(', "value": {"amount": "', lot_value_amount, '"}')
    # lot minimal step amount
    minimal_step_amount = lot_value_amount * 0.02
    minimal_step_fragment = u"{}{}{}".format(', "minimalStep": {"amount": "', minimal_step_amount, '"}')
    # lot guarantee amount
    lot_guarantee_amount = lot_value_amount * 0.004  # 0.4%
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
def tender_values(tv_number_of_lots):
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
    tender_minimal_step_json = {"amount": 100,
                                "currency": tender_currency,
                                "valueAddedTaxIncluded": valueAddedTaxIncluded
                                }
    tender_minimal_step = u"{}{}".format(', "minimalStep": ', json.dumps(tender_minimal_step_json))
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
        '"03000000-1"', u'"Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та\
        супутня продукція"'],
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
def tender_period(accelerator):
    kiev_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]
    # tender_start_date
    tender_start_date = datetime.now().strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
    # tender_end_date
    date_day = datetime.now() + timedelta(minutes=int(round(31 * (1440.0 / accelerator)) + 1))
    tender_end_date = date_day.strftime('"%Y-%m-%dT%H:%M:%S{}"'.format(kiev_now))
    tender_period_data = u"{}{}{}{}{}{}".format(
        ', "tenderPeriod": {', '"startDate": ', tender_start_date, ', "endDate": ', tender_end_date, '}')
    return tender_period_data


def tender_titles():
    tender_random_title = u"{}{}".format(u'Тест ', datetime.now().strftime('%d-%H%M%S"'))
    tender_title = u'{}{}"'.format(', "title": "', fake.text(100))  # ', "title": "', tender_random_title
    tender_description = u"{}{}{}".format(', "description": ', u'"Примечания для тендера ', tender_random_title)
    tender_title_en = u"{}{}".format(', "title_en": ', '"Title of tender in english"')
    tender_description_en = u"{}{}".format(', "description_en": ', '""')
    tender_title_description = u'{}{}{}{}'.format(tender_title, tender_description, tender_title_en,
                                                  tender_description_en)
    return tender_title_description


tender_features = u"{}{}".format(', "features": ', '[ ]')


def procuring_entity():
    procuring_entity_json = {"name": "Тестовая организация ООО Тест",
                             "name_en": "Company name en english",
                             "address": {
                                   "countryName": "Україна",
                                   "region": "місто Київ",
                                   "locality": fake.city(),
                                   "streetAddress": fake.street_address(),
                                   "postalCode": fake.postcode()
                             },
                             "contactPoint": {
                                   "name": fake.name(),
                                   "email": "testik@gmail.test",
                                   "telephone": "+380002222222",
                                   "url": "http://www.site.site",
                                   "name_en": "Name of person in english"
                             },
                             "identifier": {
                                   "id": "1111111111",
                                   "scheme": "UA-EDR",
                                   "legalName": "Тестовая организация ООО Тест",
                                   "legalName_en": fake.company()
                             },
                             "kind": "defense"
                             }
    procuring_entity_block = u"{}{}".format(
        ', "procuringEntity": ', json.dumps(procuring_entity_json))
    return procuring_entity_block


def tender_data(procurement_method, accelerator):
    procurement_method_type = ', "procurementMethodType": "{}"'.format(procurement_method)
    mode = ', "mode": "test"'
    if procurement_method == 'esco':
        submission_method_details = ', "submissionMethodDetails": "quick(mode:no-auction)"'
    else:
        submission_method_details = ', "submissionMethodDetails": "quick(mode:fast-forward)"'
    procurement_method_details = ', "procurementMethodDetails": "quick, accelerator={}"'.format(accelerator)
    status = ', "status": "draft"'
    constant_tender_data = u'{}{}{}{}{}{}{}'.format(
        tender_period(accelerator), procuring_entity(), procurement_method_type, mode, submission_method_details,
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
