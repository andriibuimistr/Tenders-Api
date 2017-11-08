# -*- coding: utf-8 -*-
import random
import os
import binascii
from datetime import datetime, timedelta
import key


# GLOBAL VARIABLES
host = "https://lb.api-sandbox.openprocurement.org"
api_version = "2.3"
auth_key = key.auth_key

tender_byustudio_host = 'http://tender.byustudio.in.ua'


def tender_currency():
    return random.choice(['"UAH"', '"USD"', '"EUR"', '"RUB"'])  # '"GBP"'
tender_currency = tender_currency()

valueAddedTaxIncluded = str(random.choice([True, False])).lower()


# INPUTS
# number of lots from user
def number_of_lots():
    number_of_lots_from_user = (raw_input(
        'Введите количество лотов (от 1 до 10, 0 - безлотовая закупка)')).decode('utf-8')
    while number_of_lots_from_user.isdigit() is not True or int(number_of_lots_from_user) > 10:
        number_of_lots_from_user = raw_input(
            'Введите правильное значение (от 1 до 10, 0 - безлотовая закупка)').decode('utf-8')
    else:
        number_of_lots_from_user = int(number_of_lots_from_user)
    return number_of_lots_from_user


# number of items from user
def number_of_items():
    number_of_items_from_user = (raw_input('Введите количество предметов закупки (от 1 до 10)')).decode('utf-8')
    while number_of_items_from_user.isdigit() is not True\
            or int(number_of_items_from_user) < 1 or int(number_of_items_from_user) > 10:
        number_of_items_from_user = raw_input('Введите правильное значение (от 1 до 10)').decode('utf-8')
    else:
        number_of_items_from_user = int(number_of_items_from_user)
    return number_of_items_from_user


# SELECT PROCUREMENT METHOD
above_threshold_procurement = [
    'aboveThresholdUA', 'aboveThresholdEU', 'aboveThresholdUA.defense', 'competitiveDialogueUA',
    'competitiveDialogueEU']
below_threshold_procurement = ['open_belowThreshold']
limited_procurement = ['limited_reporting', 'limited_negotiation', 'limited_negotiation.quick']


# Procurement method from user
def procurement_method_selector():
    # print list of procurement methods
    for method in range(len(above_threshold_procurement)):
        print '{}{}{}'.format(above_threshold_procurement[method], ' - ', method + 1)
    for method in range(len(below_threshold_procurement)):
        print '{}{}{}'.format(below_threshold_procurement[method], ' - ', method + 1 + len(above_threshold_procurement))
    for method in range(len(limited_procurement)):
        print '{}{}{}'.format(limited_procurement[method], ' - ',
                              method + 1 + len(above_threshold_procurement + below_threshold_procurement))
    # get procurement method from user
    procurement_method_from_user = (raw_input(
        'Необходимо выбрать тип процедуры, указав ее номер: ')).decode('utf-8')
    while procurement_method_from_user.isdigit() is not True or int(procurement_method_from_user) < 1 or \
            int(procurement_method_from_user) > len(
                                above_threshold_procurement + below_threshold_procurement + limited_procurement):
        procurement_method_from_user = raw_input('Введите правильное значение: ').decode('utf-8')
    else:
        procurement_method_from_user = int(procurement_method_from_user)
        if len(above_threshold_procurement) + 1 > procurement_method_from_user > 0:
            selected_procurement_method = above_threshold_procurement[procurement_method_from_user - 1]
        elif procurement_method_from_user == len(above_threshold_procurement + below_threshold_procurement):
            selected_procurement_method = below_threshold_procurement[0]
        else:
            selected_procurement_method = limited_procurement[procurement_method_from_user - (
                len(above_threshold_procurement + below_threshold_procurement) + 1)]
        return selected_procurement_method


# ITEMS
items_m = ', "items": '


# generate item description
def description_of_item(number_of_lots, number_of_items):
    description_text = [u'"Описание предмета закупки ']
    description_item = []
    if number_of_lots == 0:
        items_count = 0
        for item in range(number_of_items):
            items_count += 1
            item_description = u"{}{}{}{}".format('"description": ', random.choice(description_text), items_count, '"')
            description_item.append(item_description)
        return description_item
    else:
        items_count = 0
        for item in range(number_of_lots):
            items_count += 1
            item_description = u"{}{}{}{}{}".format(', "description": ', random.choice(description_text),
                                                    u'Лот ', items_count, '"')
            description_item.append(item_description)
        return description_item


# generate delivery address
def delivery_address_block():
    delivery_postal_code = '"12345"'
    delivery_country_name = random.choice([u'"Україна"'])
    delivery_street_address = random.choice([u'"Улица 1"', u'"Улица 2"', u'"Улица 3"'])
    delivery_region = random.choice([u'"Вінницька область"', u'"Волинська область"', u'"Дніпропетровська область"'])
    delivery_locality = random.choice([u'"Город 1"', u'"Город 2"', u'"Город 3"'])
    delivery_address = u"{}{}{}{}{}{}{}{}{}{}{}{}".format(
        ', "deliveryAddress": {', ' "postalCode": ', delivery_postal_code, ', "countryName": ', delivery_country_name,
        ', "streetAddress": ', delivery_street_address, ', "region": ', delivery_region, ', "locality": ',
        delivery_locality, " }")
    return delivery_address


# generate delivery start date
def delivery_start_date():
    week = timedelta(days=7)
    date_now = datetime.now()
    date_week = date_now + week
    return date_week.strftime('"%Y-%m-%dT%H:%M:%S+03:00"')


# generate delivery end date
def delivery_end_date():
    month = timedelta(days=30)
    date_now = datetime.now()
    date_month = date_now + month
    return date_month.strftime('"%Y-%m-%dT%H:%M:%S+03:00"')


# delivery date
deliveryDate = u"{}{}{}{}{}{}".format(
    ', "deliveryDate": {', ' "startDate": ', delivery_start_date(), ', "endDate": ', delivery_end_date(), " }")


# generate id for item(s)
def item_id_generator():
    item_id_generated = "{}{}{}".format(', "id": "', (binascii.hexlify(os.urandom(16))), '"')
    return item_id_generated


# generate unit
def unit():
    unit_code = random.choice([['"BX"', u'"ящик"'], ['"D64"', u'"блок"'], ['"E48"', u'"послуга"']])
    unit_fragment = u"{}{}{}{}{}{}".format(', "unit": {', ' "code": ', unit_code[0], ', "name": ', unit_code[1], ' }')
    return unit_fragment


# quantity
quantity = u"{}{}{}{}".format(', "quantity": ', '"', random.randint(1, 99999), '"')


# generate data for item
def item_data(number_of_lots, number_of_items, i):
    data_for_item = u'{}{}{}{}{}{}{}{}{}'.format(
        description_of_item(number_of_lots, number_of_items)[i], classification, additionalClassifications,
        description_en(), delivery_address_block(),
        deliveryDate, item_id_generator(), unit(), quantity)
    return data_for_item


# --LOTS-- ###############
lots_m = ', "lots":'
lots_close = ''


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


# TENDERS
# tender values
def tender_values(number_of_lots):
    if number_of_lots == 0:
        tender_value_amount = lot_values[1]
    else:
        tender_value_amount = lot_values[1] * number_of_lots
    tender_value = u"{}{}{}{}{}{}{}{}".format(
        '"value": {', '"valueAddedTaxIncluded": ', valueAddedTaxIncluded, ', "amount": ', tender_value_amount,
        ', "currency": ', tender_currency, '}')
    tender_guarantee = u"{}{}{}{}{}{}{}".format(', "guarantee": {"amount": ', '"', '0', '"', ', "currency": ',
                                                tender_currency, '}')
    tender_minimal_step = u"{}{}{}{}{}{}{}{}".format(
        ', "minimalStep": {', '"amount": ', '"100"', ', "currency": ', tender_currency, ', "valueAddedTaxIncluded": ',
        valueAddedTaxIncluded, '}')
    values_of_tender = '{}{}{}'.format(tender_value, tender_guarantee, tender_minimal_step)
    return values_of_tender
# from tender - tender_values = tender_values(number_of_lots)


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

additionalClassifications = ', "additionalClassifications": [ ]'


# random tender description from list
def description_en():
    description_en_text = ['"Description 1"', '"Description 2"', '"Description 3"']
    description_en_fragment = u"{}{}".format(', "description_en": ', random.choice(description_en_text))
    return description_en_fragment


# Generate tender period
def tender_period():
    # tender_start_date
    date_now = datetime.now()
    tender_start_date = date_now.strftime('"%Y-%m-%dT%H:%M:%S+02:00"')
    # tender_end_date
    day = timedelta(minutes=31)  # input(u'Дата окончания приема предложений ( в минутах): ')
    date_now = datetime.now()
    date_day = date_now + day
    tender_end_date = date_day.strftime('"%Y-%m-%dT%H:%M:%S+02:00"')
    tender_period_data = u"{}{}{}{}{}{}".format(
        ', "tenderPeriod": {', '"startDate": ', tender_start_date, ', "endDate": ', tender_end_date, '}')
    return tender_period_data


def tender_titles():
    tender_number = datetime.now().strftime('%d-%H%M%S"')
    tender_random_title = u"{}{}".format(u'Тест ', tender_number)
    tender_title = u"{}{}".format(', "title": "', tender_random_title)
    tender_description = u"{}{}{}".format(', "description": ', u'"Примечания для тендера ', tender_random_title)
    tender_title_en = u"{}{}".format(', "title_en": ', '"Title of tender in english"')
    tender_description_en = u"{}{}".format(', "description_en": ', '""')
    tender_title_description = u'{}{}{}{}'.format(tender_title, tender_description, tender_title_en,
                                                  tender_description_en)
    return tender_title_description

tender_features = u"{}{}".format(', "features": ', '[ ]')


def procuring_entity():
    company_name = u'"Тестовая организация ООО Тест"'
    company_name_en = '"Company name en english"'
    name = u"{}{}".format('"name": ', company_name)
    name_en = u"{}{}".format(', "name_en": ', company_name_en)
    country_name = u'"Україна"'
    region = u'"місто Київ"'
    locality = u'"Киев"'
    street_address = u'"Улица"'
    postal_code = '"01234"'
    address = u"{}{}{}{}{}{}{}{}{}{}{}{}".format(
        ', "address": {', '"countryName": ', country_name, ', "region": ', region, ', "locality": ', locality,
        ', "streetAddress": ', street_address, ', "postalCode": ', postal_code, '}')
    contact_name = u'"Теркин Василий Васильевич"'
    email = '"formyqatesting@gmail.com"'
    telephone = '"+380002222222"'
    url = '"http://www.site.site"'
    contact_name_en = u'"Name of person in english"'
    contact_point = u"{}{}{}{}{}{}{}{}{}{}{}{}".format(
        ', "contactPoint": {', '"name": ', contact_name, ', "email": ', email, ', "telephone": ', telephone,
        ', "url": ', url, ', "name_en": ', contact_name_en, '}')
    identifier = u"{}{}{}{}{}".format(
        ', "identifier": { "id": "1111111111", "scheme": "UA-EDR", "legalName": ', company_name, ', "legalName_en":',
        company_name_en, '}')
    kind = ', "kind": "defense"'
    procuring_entity_block = u"{}{}{}{}{}{}{}{}".format(
        ', "procuringEntity": {', name, name_en, address, contact_point, identifier, kind, '}')
    return procuring_entity_block


def tender_data(procurement_method):
    procurement_method_type = ', "procurementMethodType": "{}"'.format(procurement_method)
    mode = ', "mode": "test"'
    submission_method_details = ', "submissionMethodDetails": "quick(mode:fast-forward)"'
    procurement_method_details = ', "procurementMethodDetails": "quick, accelerator=1440"'
    status = ', "status": "draft"'
    constant_tender_data = u'{}{}{}{}{}{}{}'.format(tender_period(), procuring_entity(), procurement_method_type, mode,
                                                    submission_method_details, procurement_method_details, status)
    return constant_tender_data


# VARIABLES FOR BID
# Above threshold procedures with active bid status
above_threshold_active_bid_procurements = ['aboveThresholdUA', 'aboveThresholdUA.defense']
