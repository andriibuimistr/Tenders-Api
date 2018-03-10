# -*- coding: utf-8 -*-
from faker import Faker
from random import randint
import pytz
from datetime import datetime, timedelta
import binascii
import os


fake = Faker('uk_UA')

kiev_utc_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


def dgf_decision_date(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def auction_period_start_date(accelerator):
    return (datetime.now() + timedelta(minutes=10*(1440/accelerator))).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_utc_now))  # standard period is 10 minutes if accelerator == 1440


def auction_value():
    generated_value = randint(1000, 10000)
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


def generate_id_for_item():
    return binascii.hexlify(os.urandom(16))


def generate_items_for_auction(number_of_items):
    items = []
    count = 0
    for item in range(number_of_items):
        count += 1
        item_json = {
                        "description": "Предмет {} {}".format(count, fake.text(100).replace('\n', ' ')),
                        "classification": {
                            "scheme": "CAV",
                            "description": "Права вимоги за кредитними договорами",
                            "id": "07000000-9"
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


def generate_auction_json(procurement_method_type, number_of_items, accelerator):
    values = auction_value()
    auction_data = {"data": {
                        "procurementMethod": "open",
                        "submissionMethod": "electronicAuction",
                        "dgfDecisionDate": dgf_decision_date(1),
                        "procurementMethodType": procurement_method_type,
                        "dgfDecisionID": "ID-123-456-789-0",
                        "description": fake.text(200).replace('\n', ' '),
                        "title": fake.text(100).replace('\n', ' '),
                        "tenderAttempts": randint(1, 8),
                        "auctionPeriod": {
                            "startDate": auction_period_start_date(accelerator),
                        },
                        "guarantee": values[1],
                        "status": "draft",
                        "procurementMethodDetails": "quick, accelerator={}".format(accelerator),
                        "title_en": "[TESTING] Title in English",
                        "dgfID": "N-1234567890",
                        "submissionMethodDetails": "quick",
                        "items": generate_items_for_auction(number_of_items),
                        "value": values[0],
                        "minimalStep": values[2],
                        "mode": "test",
                        "title_ru": "[ТЕСТИРОВАНИЕ] Заголовок на русском",
                        "procuringEntity": {
                            "contactPoint": {
                                "telephone": "+38(000)044-45-80",
                                "name": "Гоголь Микола Васильович",
                                "email": "test@test.test"
                            },
                            "identifier": {
                                "scheme": "UA-EDR",
                                "id": "12345680",
                                "legalName": "Тестовый организатор \"Банк Ликвидатор\""
                            },
                            "name": "Тестовый организатор \"Банк Ликвидатор\"",
                            "kind": "general",
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
    return auction_data
