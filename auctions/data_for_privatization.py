# -*- coding: utf-8 -*-
from faker import Faker
from random import randint
import pytz
from datetime import datetime, timedelta
import binascii
import os

fake = Faker('uk_UA')
kiev_utc_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


def decision_date():
    return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_utc_now))


def generate_id_for_item():
    return binascii.hexlify(os.urandom(16))


def generate_items_for_asset(number_of_items):
    items = []
    count = 0
    for item in range(number_of_items):
        count += 1
        item_json = {
                        "registrationDetails": {
                            "status": "registering"
                        },
                        "description": "Предмет {} {}".format(count, fake.text(100).replace('\n', ' ')),
                        "classification": {
                            "scheme": "CAV-PS",
                            "description": "Котедж",
                            "id": "04151000-1"
                        },
                        "address": {
                            "postalCode": "04655",
                            "countryName": "Україна",
                            "streetAddress": "вулиця Редьчинська, 30",
                            "region": "місто Київ",
                            "locality": "Київ"
                        },
                        "id": generate_id_for_item(),
                        "unit": {
                            "code": "E48",
                            "name": "послуга"
                        },
                        "quantity": randint(1, 1000)
                    }
        items.append(item_json)
    return items


def generate_asset_json(number_of_items):
    asset_data = {"data": {
                        "decisions": [
                            {
                                "decisionID": "1637-10",
                                "title": fake.text(50).replace('\n', ' '),
                                "decisionDate": decision_date(),
                            }
                        ],
                        "status": "draft",
                        "assetType": "domain",
                        "description": fake.text(200).replace('\n', ' '),
                        "title": fake.text(100).replace('\n', ' '),
                        "items": generate_items_for_asset(number_of_items),
                        "mode": "test",
                        "assetCustodian": {
                            "additionalContactPoints": [
                                {
                                    "telephone": "426-07-12",
                                    "url": "https://www.google.com.ua",
                                    "faxNumber": "413-41-40",
                                    "name": "Гоголь Микола Васильович",
                                    "email": "test@test.test"
                                }
                            ],
                            "contactPoint": {
                                "telephone": "+380220000000",
                                "url": "https://www.google.com.ua",
                                "faxNumber": "380512508818",
                                "name": "Гоголь Олександр Васильович",
                                "email": "test@test.com"
                            },
                            "identifier": {
                                "scheme": "UA-EDR",
                                "id": "01010122",
                                "legalName": "ТОВ Орган Приватизации"
                            },
                            "name": "ТОВ Орган Приватизации",
                            "address": {
                                "postalCode": "00000",
                                "countryName": "Україна",
                                "streetAddress": "ул. Койкого 325",
                                "region": "місто Київ",
                                "locality": "Киев"
                            }
                        },
                        "assetHolder": {
                            "additionalContactPoints": [
                                {
                                    "telephone": "426-07-12",
                                    "url": "https://www.google.com",
                                    "faxNumber": "413-41-40",
                                    "name": "Гоголь Олександр",
                                    "email": "kmkshvl@ukr.net"
                                }
                            ],
                            "contactPoint": {
                                "telephone": "+380221112233",
                                "url": "https://www.google.com",
                                "faxNumber": "380512508818",
                                "name": "Рустам Коноплянка",
                                "email": "test@test.com"
                            },
                            "identifier": {
                                "scheme": "UA-EDR",
                                "id": "01010122",
                                "legalName": "ТОВ Орган Приватизации"
                            },
                            "name": "ТОВ Орган Приватизации",
                            "address": {
                                "postalCode": "00000",
                                "countryName": "Україна",
                                "streetAddress": "ул. Койкого 325",
                                "region": "місто Київ",
                                "locality": "Киев"
                            }
                            }
                        }
                  }
    return asset_data
