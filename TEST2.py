# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from faker import Faker
from random import randint, choice
import pytz
import binascii
import os
from pprint import pprint
import json

fake = Faker('uk_UA')
kiev_utc_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


def generate_id_for_item():
    return binascii.hexlify(os.urandom(16))


def generate_id_for_lot(number_of_lots):
    list_of_id = []
    for x in range(number_of_lots):
        list_of_id.append(binascii.hexlify(os.urandom(16)))
    return list_of_id


def generate_values(procurement_method, number_of_lots):
    generated_value = randint(100000, 1000000000)
    value = {
        "currency": "UAH",
        "amount": generated_value,
        "valueAddedTaxIncluded": True
    }
    guarantee = {
        "currency": "UAH",
        "amount": '{0:.2f}'.format(generated_value * 0.05)
    }
    minimal_step = {
        "currency": "UAH",
        "amount": '{0:.2f}'.format(generated_value * 0.01),
        "valueAddedTaxIncluded": True
    }
    return value, guarantee, minimal_step


def generate_items(number_of_items, procurement_method):
    items = []
    unit = choice([['"BX"', u'"ящик"'], ['"D64"', u'"блок"'], ['"E48"', u'"послуга"']])
    classification = choice([['"03000000-1"', u'"Сільськогосподарська, фермерська продукція, продукція рибальства, лісівництва та супутня продукція"'],
                             ['"09000000-3"', u'"Нафтопродукти, паливо, електроенергія та інші джерела енергії"'],
                             ['"14000000-1"', u'"Гірнича продукція, неблагородні метали та супутня продукція"']])
    item_number = 0
    for item in range(number_of_items):
        item_number += 1
        item_data = {
                    "description": "Предмет закупки {}{}".format(item_number, fake.text(200).replace('\n', ' ')),
                    "classification": {
                        "scheme": "ДК021",
                        "description": classification[1],
                        "id": classification[0]
                    },
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
        if procurement_method == 'esco':
            del(item_data['deliveryDate'])
            del(item_data['unit'])
            del (item_data['quantity'])
        items.append(item_data)
    return items


def generate_lots(lots_id, procurement_method):
    lots = []
    lot_number = 0
    for lot in range(len(lots_id)):
        lot_number += 1
        lots_data = {
                    "status": "active",
                    "description": "Описание лота Лот {} {}".format(lot_number, fake.text(200).replace('\n', ' ')),
                    "title": "Лот {}".format(lot_number),
                    "minimalStep": {# !!!!!!!!!!!!!!!!!!
                        "currency": "EUR",
                        "amount": 672.25,
                        "valueAddedTaxIncluded": True
                    },
                    "title_en": "Title of lot in English",
                    "description_en": "Description of lot in English",
                    "value": {#!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        "currency": "EUR",
                        "amount": 67225,
                        "valueAddedTaxIncluded": True
                    },
                    "id": lots_id[lot],
                    "guarantee": {####################
                        "currency": "EUR",
                        "amount": 1344.5
                    }
                }
        lots.append(lots_data)
    return lots


def generate_tender_json(procurement_method, number_of_lots, number_of_items, accelerator, received_tender_status):
    tender_data = {
                    "data": {
                        "procurementMethodType": procurement_method,
                        "description": "Примечания для тендера Тест {}".format(datetime.now().strftime('%d-%H%M%S"')),
                        "title": fake.text(200).replace('\n', ' '),
                        "guarantee": {####
                            "currency": "EUR",
                            "amount": 2689
                        },
                        "status": "draft",
                        "tenderPeriod": {######################
                            "startDate": "2018-03-18T18:01:06+02:00",
                            "endDate": "2018-03-18T18:33:06+02:00"
                        },
                        "procurementMethodDetails": "quick, accelerator={}".format(accelerator),
                        "title_en": "Title of tender in english",
                        "description_en": "",
                        "submissionMethodDetails": "quick(mode:fast-forward)",
                        "value": {###############
                            "currency": "EUR",
                            "amount": 134450,
                            "valueAddedTaxIncluded": True
                        },
                        "minimalStep": {####################
                            "currency": "EUR",
                            "amount": 672.25,
                            "valueAddedTaxIncluded": True
                        },
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
    items = []
    if number_of_lots == 0:
        items = generate_items(number_of_items, procurement_method)
        tender_data['data']['items'] = items
    else:
        list_of_lots_id = generate_id_for_lot(number_of_lots)
        lots = generate_lots(list_of_lots_id, procurement_method)
        for lot in range(number_of_lots):
            lot_items = generate_items(number_of_items, procurement_method)
            for item in range(len(lot_items)):
                lot_items[item]['description'] = "Предмет закупки {} Лот {}".format(item + 1, lot + 1)
                lot_items[item]['relatedLot'] = list_of_lots_id[lot]
                items.append(lot_items[item])
        tender_data['data']['items'] = items
        tender_data['data']['lots'] = lots
    return tender_data
