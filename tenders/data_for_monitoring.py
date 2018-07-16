# -*- coding: utf-8 -*-
from datetime import timedelta
from tenders.tender_additional_data import *
from faker import Faker

fake = Faker('uk_UA')


def decision_date():
    return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_now))


def generate_monitoring_json(tender_id_long, accelerator):
    monitoring_data = {"data": {
                            "reasons": [
                              "public",
                              "fiscal"
                            ],
                            "tender_id": tender_id_long,
                            "procuringStages": [
                              "awarding",
                              "contracting"
                            ],
                            "monitoringDetails": "accelerator={}".format(accelerator),
                            "parties": [
                              {
                                "contactPoint": {
                                  "name": "Oleksii Kovalenko",
                                  "telephone": "0440000000"
                                },
                                "identifier": {
                                  "scheme": "UA-EDR",
                                  "id": "40165856",
                                  "uri": "http://www.dkrs.gov.ua"
                                },
                                "name": "The State Audit Service of Ukraine",
                                "roles": [
                                  "sas"
                                ],
                                "address": {
                                  "countryName": "Ukraine",
                                  "postalCode": "04070",
                                  "region": "Kyiv",
                                  "streetAddress": "Petra Sahaidachnoho St, 4",
                                  "locality": "Kyiv"
                                }
                              }
                            ]
                          }
                       }
    return monitoring_data


def generate_decision(document):
    document['data']['title'] = 'Документ для рішення про початок моніторингу (Document for decision)'
    decision = {"data": {
                    "decision": {
                      "date": decision_date(),
                      "description": fake.text(500).replace('\n', ' '),
                      "documents": [document['data']]
                    }
                  }
                }
    return decision


def generate_conclusion_true(document):
    document['data']['title'] = 'Документ для висновку. Порушення виявлені (Document for conclusion, status TRUE)'
    conclusion = {"data": {
                        "conclusion": {
                              "violationType": [
                                    "documentsForm",
                                    "corruptionAwarded"
                              ],
                              "description": fake.text(500).replace('\n', ' '),
                              "stringsAttached": fake.text(50).replace('\n', ' '),
                              "auditFinding": fake.text(50).replace('\n', ' '),
                              "violationOccurred": True,
                              "documents": [document['data']]
                            }
                        }
                  }
    return conclusion


def generate_conclusion_false(document):
    document['data']['title'] = 'Документ для висновку. Порушення не виявлені (Document for conclusion, status FALSE)'
    conclusion = {"data": {
                        "conclusion": {
                          "violationOccurred": False,
                          "documents": [document['data']]
                        }
                      }
                  }
    return conclusion


def generate_json_for_post(document):
    document['data']['title'] = 'Документ для пояснення (Document for post)'
    post = {"data": {
                    "title": fake.text(50).replace('\n', ' '),
                    "description": fake.text(200).replace('\n', ' '),
                    "documents": [document['data']]
                  }
            }
    return post
