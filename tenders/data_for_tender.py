# -*- coding: utf-8 -*-
from dk021 import classification_dk021, additional_class_scheme, additional_class_003, additional_class_015, additional_class_018, additional_class_INN
import binascii
import os
from random import randint, choice
import pytz
from faker import Faker
from datetime import datetime, timedelta
from tenders.tender_additional_data import kiev_now, limited_procurement, negotiation_procurement


fake = Faker('uk_UA')
kiev_utc_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


# Contracts
def activate_contract_json(complaint_end_date):
    contract_end_date = datetime.now() + timedelta(days=120)
    complaint_end_date = datetime.strptime(complaint_end_date, '%Y-%m-%dT%H:%M:%S.%f{}'.format(kiev_now))
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


def get_classification():
    classification_section = {"classification": {
        "scheme": "ДК021",
        "description": '',
        "id": ''
    }}
    main_classification = []
    cl = choice(classification_dk021)
    for x in cl:
        main_classification = [x, cl[x]]
    if '33600000-6' in main_classification or '99999999-9' in main_classification:
        classification_section["additionalClassifications"] = []
        additional_classification_scheme = ''
        random_ad_class = ''
        if '99999999-9' in main_classification:
            additional_classification_scheme = choice(additional_class_scheme)
            random_ad_class = {"000": "Спеціальні норми та інше"}
            if additional_classification_scheme == 'ДК003':
                random_ad_class = choice(additional_class_003)
            elif additional_classification_scheme == 'ДК015':
                random_ad_class = choice(additional_class_015)
            elif additional_classification_scheme == 'ДК018':
                random_ad_class = choice(additional_class_018)
            else:
                additional_classification_scheme = 'specialNorms'
        elif '33600000-6' in main_classification:
            additional_classification_scheme = "INN"
            random_ad_class = choice(additional_class_INN)
        classification_section["additionalClassifications"].append({
                                                                        "scheme": additional_classification_scheme,
                                                                        "id": random_ad_class.keys()[0],
                                                                        "description": random_ad_class[random_ad_class.keys()[0]]
                                                                    })

    classification_section['classification']['description'] = main_classification[1]
    classification_section['classification']['id'] = main_classification[0]
    return classification_section


def get_unit():
    return choice([['BX', u'ящик'], ['D64', u'блок'], ['E48', u'послуга']])


def generate_id_for_item():
    return binascii.hexlify(os.urandom(16))


def generate_id_for_lot(number_of_lots):
    list_of_id = []
    for x in range(number_of_lots):
        list_of_id.append(binascii.hexlify(os.urandom(16)))
    return list_of_id


def tender_period(accelerator, procurement_method, received_tender_status):
    # tender_start_date
    tender_start_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
    # tender_end_date
    date_day = datetime.now() + timedelta(minutes=int(round(31 * (1440.0 / accelerator)) + 1))
    tender_end_date = date_day.strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
    tender_period_data = {"tenderPeriod": {
                                    "startDate": tender_start_date,
                                    "endDate": tender_end_date
    }}

    if procurement_method == 'belowThreshold':
        one_day = datetime.now() + timedelta(minutes=int(round(1 * (1440.0 / accelerator))), seconds=10)
        ten_days = datetime.now() + timedelta(minutes=int(round(10 * (1440.0 / accelerator))), seconds=10)
        five_dozens_days = datetime.now() + timedelta(minutes=int(round(60 * (1440.0 / accelerator))), seconds=10)
        tender_start_date = one_day.strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
        tender_end_date = five_dozens_days.strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
        if received_tender_status == 'active.qualification':
            tender_end_date = ten_days.strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
        tender_period_data = {"tenderPeriod": {
                                    "startDate": tender_start_date,
                                    "endDate": tender_end_date
        },
                             "enquiryPeriod": {
                                    "startDate": datetime.now().strftime('%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now)),
                                    "endDate": tender_start_date
                            }}
    return tender_period_data


def generate_features(tender_data):
    if 'lots' in tender_data['data']:
        number_of_lots = len(tender_data['data']['lots'])
    else:
        number_of_lots = 0

    features = [{
                "code": generate_id_for_item(),
                "description": "Описание неценового критерия для тендера",
                "title": "Неценовой критерий для тендера",
                "enum": [],
                "title_en": "Feature of tender",
                "description_en": "Description of feature for tender",
                "featureOf": "tenderer"
                }]
    feature_number = -1
    for feature in range(6):
        feature_number += 1
        feature = {
                        "title_en": "Feature option {}".format(feature_number + 1),
                        "value": float('0.0{}'.format(feature_number)),
                        "title": "Опция {} {}".format(feature_number + 1, fake.text(20).replace('\n', ' '))
                    }
        features[0]['enum'].append(feature)

    if number_of_lots == 0:
        features = features
    else:
        for lot in range(number_of_lots):
            lot_feature = {
                            "code": generate_id_for_item(),
                            "description": "Описание неценового критерия Лот {}".format(lot + 1),
                            "title": "Неценовой критерий Лот {}".format(lot + 1),
                            "enum": [],
                            "title_en": "Title of feature for lot {}".format(lot + 1),
                            "description_en": "Description of feature for lot {}".format(lot + 1),
                            "relatedItem": tender_data['data']['lots'][lot]['id'],
                            "featureOf": "lot"
                        }
            feature_number = -1
            for feature in range(6):
                feature_number += 1
                feature = {
                    "title_en": "Feature option {}".format(feature_number + 1),
                    "value": float('0.0{}'.format(feature_number)),
                    "title": "Опция {} Лот {} {}".format(feature_number + 1, lot + 1, fake.text(20).replace('\n', ' '))
                }
                lot_feature['enum'].append(feature)
            features.append(lot_feature)
    return features


def generate_values(procurement_method, number_of_lots):
    if not number_of_lots:
        number_of_lots = 1
    generated_value = randint(100000, 1000000000)
    currency = choice(['UAH', 'USD', 'EUR', 'RUB'])  # 'GBP'
    if procurement_method == 'esco':
        value = {"tenderValues": {
                            "NBUdiscountRate": 0.99,
                            "yearlyPaymentsPercentageRange": 0.8,
                            "minimalStepPercentage": 0.02},
                 "lotValues": {
                            "yearlyPaymentsPercentageRange": 0.8,
                            "minimalStepPercentage": 0.02}
                 }
    else:
        value = {"tenderValues": {
                            "value": {
                                "currency": currency,
                                "amount": generated_value,
                                "valueAddedTaxIncluded": True},

                            "guarantee": {
                                "currency": currency,
                                "amount": '{0:.2f}'.format(generated_value * 0.02)
                            },
                            "minimalStep": {
                                "currency": currency,
                                "amount": '{0:.2f}'.format(generated_value * 0.01),
                                "valueAddedTaxIncluded": True
                            }},
                 "lotValues": {
                            "value": {
                                "currency": currency,
                                "amount": '{0:.2f}'.format(generated_value / number_of_lots),
                                "valueAddedTaxIncluded": True},

                            "guarantee": {
                                "currency": currency,
                                "amount": '{0:.2f}'.format((generated_value * 0.02) / number_of_lots)
                            },
                            "minimalStep": {
                                "currency": currency,
                                "amount": '{0:.2f}'.format((generated_value * 0.01) / number_of_lots),
                                "valueAddedTaxIncluded": True
                            }
            }}
        if procurement_method in limited_procurement:
            del value['tenderValues']['guarantee'], value['tenderValues']['minimalStep'], value['lotValues']['guarantee'], value['lotValues']['minimalStep']
    return value


def generate_items(number_of_items, procurement_method, classification):
    unit = get_unit()
    items = []
    item_number = 0
    for item in range(number_of_items):
        item_number += 1
        item_data = {
                    "description": "Предмет закупки {} {}".format(item_number, fake.text(200).replace('\n', ' ')),
                    "description_en": "Description",
                    "deliveryAddress": {
                        "postalCode": "00000",
                        "countryName": "Україна",
                        "streetAddress": "Улица",
                        "region": "Дніпропетровська область",
                        "locality": "Город"
                    },
                    "deliveryDate": {
                        "startDate": datetime.strftime(datetime.now() + timedelta(days=7), '%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now)),
                        "endDate": datetime.strftime(datetime.now() + timedelta(days=120), '%Y-%m-%dT%H:%M:%S{}'.format(kiev_utc_now))
                    },
                    "id": generate_id_for_item(),
                    "unit": {
                        "code": unit[0],
                        "name": unit[1]
                    },
                    "quantity": randint(1, 10000)
                }
        for key in classification:
            item_data[key] = classification[key]
        if procurement_method == 'esco':
            del(item_data['deliveryDate'])
            del(item_data['unit'])
            del (item_data['quantity'])
        items.append(item_data)
    return items


def generate_lots(lots_id, values):
    lots = []
    lot_number = 0
    for lot in range(len(lots_id)):
        lot_number += 1
        lots_data = {
                    "status": "active",
                    "description": "Описание лота Лот {} {}".format(lot_number, fake.text(200).replace('\n', ' ')),
                    "title": "Лот {}".format(lot_number),
                    "title_en": "Title of lot in English",
                    "description_en": "Description of lot in English",
                    "id": lots_id[lot]
                }
        for key in values:
            lots_data[key] = values[key]
        lots.append(lots_data)
    return lots


def generate_tender_json(procurement_method, number_of_lots, number_of_items, accelerator, received_tender_status, list_of_lots_id, if_features, skip_auction):
    tender_data = {
                    "data": {
                        "procurementMethodType": procurement_method,
                        "description": "Примечания для тендера Тест {}".format(datetime.now().strftime('%d-%H%M%S')),
                        "title": fake.text(200).replace('\n', ' '),
                        "status": "draft",
                        "procurementMethodDetails": "quick, accelerator={}".format(accelerator),
                        "title_en": "Title of tender in english",
                        "description_en": "",
                        "mode": "test",
                        "title_ru": "",
                        "procuringEntity": {
                            "kind": "defense",
                            "name": "Тестовая организация ООО Тест",
                            "address": {
                                "postalCode": "12345",
                                "countryName": "Україна",
                                "streetAddress": "Улица Койкого",
                                "region": "місто Київ",
                                "locality": "Київ"
                            },
                            "contactPoint": {
                                "telephone": "+380002222222",
                                "url": "http://www.site.site",
                                "name_en": "Name of person in english",
                                "name": fake.name(),
                                "email": "testik@gmail.test"
                            },
                            "identifier": {
                                "scheme": "UA-EDR",
                                "legalName_en": fake.company(),
                                "id": "00000000",
                                "legalName": "Тестовая организация ООО Тест"
                            },
                            "name_en": "Company name en english"
                        }
                    }
                }
    classification = get_classification()

    if procurement_method not in limited_procurement:
        if skip_auction is True:
            if procurement_method == 'esco':
                submission_method_details = 'quick(mode:no-auction)'
            else:
                submission_method_details = 'quick(mode:fast-forward)'
        else:
            submission_method_details = 'quick'
        tender_data['data']['submissionMethodDetails'] = submission_method_details

    if procurement_method in negotiation_procurement:
        tender_data['data']['cause'] = 'noCompetition'
        tender_data['data']['causeDescription'] = 'Створення закупівлі для переговорної процедури за нагальною потребою'

    values = generate_values(procurement_method, number_of_lots)
    for key in values['tenderValues']:
        tender_data['data'][key] = values['tenderValues'][key]

    if procurement_method not in limited_procurement:
        tender_periods = tender_period(accelerator, procurement_method, received_tender_status)
        for key in tender_periods:
            tender_data['data'][key] = tender_periods[key]

    items = []
    if number_of_lots == 0:
        items = generate_items(number_of_items, procurement_method, classification)
        tender_data['data']['items'] = items
    else:
        lots = generate_lots(list_of_lots_id, values['lotValues'])
        for lot in range(number_of_lots):
            lot_items = generate_items(number_of_items, procurement_method, classification)
            for item in range(len(lot_items)):
                lot_items[item]['description'] = "Предмет закупки {} Лот {} {}".format(item + 1, lot + 1, fake.text(200).replace('\n', ' '))
                lot_items[item]['relatedLot'] = list_of_lots_id[lot]
                items.append(lot_items[item])
        tender_data['data']['items'] = items
        tender_data['data']['lots'] = lots

    if procurement_method not in limited_procurement:
        if if_features == 1:
            tender_data['data']['features'] = generate_features(tender_data)
    return tender_data
