# -*- coding: utf-8 -*-
from faker import Faker
from random import randint
import pytz
from datetime import datetime, timedelta


fake = Faker('uk_UA')

kiev_utc_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]


def dgf_decision_date(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")




def generate_auction_json(procurement_method_type):
    auction_data = {"data": {
                        "procurementMethod": "open",
                        "submissionMethod": "electronicAuction",
                        "dgfDecisionDate": dgf_decision_date(1),
                        "procurementMethodType": procurement_method_type,
                        "awardCriteria": "highestCost",
                        "dgfDecisionID": "njy",
                        "id": "fd96628ed604419aaeece724573f02d0",
                        "description": "Знахарювати друженько дрова перегортувати захмурытыся підсмалити пороспікатися.",
                        "title": "[ТЕСТУВАННЯ] Сужена згучатися уректи недоношениця.",
                        "tenderAttempts": randint(1, 8),
                        "auctionPeriod": {
                            "startDate": "2018-04-06T15:21:15+03:00",
                        },
                        "guarantee": {
                            "currency": "UAH",
                            "amount": 500000
                        },
                        "dateModified": "2018-03-10T15:04:55.479405+02:00",
                        "status": "draft",
                        "tenderPeriod": {
                            "startDate": "2018-03-10T15:02:40.497698+02:00",
                            "endDate": "2018-04-06T15:01:12.416666+03:00"
                        },
                        "procurementMethodDetails": "quick, accelerator=1440",
                        "title_en": "[TESTING] ",
                        "dgfID": "F61782126-95274",
                        "date": "2018-03-10T15:02:48.766903+02:00",
                        "submissionMethodDetails": "quick",
                        "items": [
                            {
                                "description": "i-b141164b: Права вимоги за кредитними договорами",
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
                                "id": "ca6adeb00c93ca3f8045c0742d01ba7d",
                                "unit": {
                                    "code": "E48",
                                    "name": "послуга"
                                },
                                "quantity": 59
                            },
                            {
                                "description": "i-62750772: Застава - Земельні ділянки",
                                "classification": {
                                    "scheme": "CAV",
                                    "description": "Застава - Земельні ділянки",
                                    "id": "07223000-8"
                                },
                                "address": {
                                    "postalCode": "51220",
                                    "countryName": "Україна",
                                    "streetAddress": "вулиця Шевченка",
                                    "region": "Дніпропетровська",
                                    "locality": "Перещепине"
                                },
                                "id": "4e5f5459db12e3ef1ce9255b2bac29ef",
                                "unit": {
                                    "code": "E48",
                                    "name": "послуга"
                                },
                                "quantity": 50
                            },
                            {
                                "description": "i-3cb5d258: Кредити Юридичних осіб беззаставні",
                                "classification": {
                                    "scheme": "CAV",
                                    "description": "Кредити Юридичних осіб беззаставні",
                                    "id": "07110000-3"
                                },
                                "address": {
                                    "postalCode": "14000",
                                    "countryName": "Україна",
                                    "streetAddress": "вулиця Хлібопекарська, 19, 11",
                                    "region": "Чернігівська",
                                    "locality": "Чернігів"
                                },
                                "id": "1a23d79f849fe02b3bd4f48c592968bf",
                                "unit": {
                                    "code": "E48",
                                    "name": "послуга"
                                },
                                "quantity": 42
                            }
                        ],
                        "value": {
                            "currency": "UAH",
                            "amount": 135756947.39,
                            "valueAddedTaxIncluded": True
                        },
                        "minimalStep": {
                            "currency": "UAH",
                            "amount": 2530435.66,
                            "valueAddedTaxIncluded": True
                        },
                        "mode": "test",
                        "title_ru": "[ТЕСТИРОВАНИЕ] ",
                        "next_check": "2018-04-06T15:01:12.416666+03:00",
                        "procuringEntity": {
                            "contactPoint": {
                                "telephone": "+38(000)044-45-80",
                                "name": "Зайченко Марина Григорівна",
                                "email": "kievgorsvet_z@ukr.net"
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
                                "streetAddress": "ул. Воздвиженская 325",
                                "region": "місто Київ",
                                "locality": "Киев"
                            }
                        }
                    }
                }
    return auction_data
