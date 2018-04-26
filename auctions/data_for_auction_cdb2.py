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
    return (datetime.now() + timedelta(minutes=8*(1440/accelerator))).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_utc_now))  # standard period is 10 minutes if accelerator == 1440


def contract_period():
    start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_utc_now))
    end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_utc_now))
    return start_date, end_date


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


def generate_items_for_auction(number_of_items, rent):
    items = []
    count = 0
    for item in range(number_of_items):
        count += 1
        item_json = {
                        "description": "Предмет {} {}".format(count, fake.text(100).replace('\n', ' ')),
                        "classification": {
                            "scheme": "CPV",
                            "description": "Сільськогосподарські культури, продукція товарного садівництва та рослинництва",
                            "id": "03110000-5"
                        },
                        "address": {
                            "postalCode": "00000",
                            "countryName": "Україна",
                            "streetAddress": "ул. Койкого 325",
                            "region": "місто Київ",
                            "locality": "Киев"
                        },
                        "id": generate_id_for_item(),
                        "unit": {
                            "code": "MTK",
                            "name": "метри квадратні"
                        },
                        "quantity": randint(1, 1000)
                    }
        if rent is True:
            period = contract_period()
            item_json["contractPeriod"] = {
                                            "startDate": period[0],
                                            "endDate": period[1]
                                        }
            item_json["additionalClassifications"] = [
                                                        {
                                                            "scheme": "CPVS",
                                                            "id": "PA01-7",
                                                            "description": "Оренда"
                                                        }
                                                     ]

        items.append(item_json)
    return items


def generate_auction_json_cdb_2(number_of_items, accelerator, minNumberOfQualifiedBids, rent, skip_auction):
    values = auction_value()
    auction_data = {"data": {
                        "procurementMethod": "open",
                        "submissionMethod": "electronicAuction",
                        "description": fake.text(200).replace('\n', ' '),
                        "title": fake.text(100).replace('\n', ' '),
                        "tenderAttempts": randint(1, 4),
                        "guarantee": values[1],
                        "procurementMethodDetails": "quick, accelerator={}".format(accelerator),
                        "procurementMethodType": "dgfOtherAssets",
                        "dgfID": "N-1234567890",
                        "submissionMethodDetails": "quick{}".format(skip_auction),
                        "items": generate_items_for_auction(number_of_items, rent),
                        "value": values[0],
                        "minimalStep": values[2],
                        "mode": "test",
                        "awardCriteria": "highestCost",
                        "auctionPeriod": {
                            "startDate": auction_period_start_date(accelerator),
                        },
                        "procuringEntity": {
                            "contactPoint": {
                                "telephone": "+38(222)222-22-22",
                                "name": "Иващенко Василь Петрович",
                                "email": "test@test.test"
                            },
                            "identifier": {
                                "scheme": "UA-EDR",
                                "id": "12364861",
                                "legalName": "Тестовый \"Замовник Тест\" 2"
                            },
                            "name": "Тестовый \"Замовник Тест\" 2",
                            "kind": "other",
                            "address": {
                                "postalCode": "12358",
                                "countryName": "Україна",
                                "streetAddress": "Адрес",
                                "region": "Тернопільська область",
                                "locality": "Тернополь"
                            }
                        }
                    }
                    }
    if rent is True:
        auction_data["data"]["minNumberOfQualifiedBids"] = minNumberOfQualifiedBids
    return auction_data
