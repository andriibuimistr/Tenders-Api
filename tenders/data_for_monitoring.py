# -*- coding: utf-8 -*-
from datetime import timedelta
from tenders.tender_additional_data import *


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
                      "description": "Описание decision",
                      "documents": [document['data']]
                    }
                  }
                }
    return decision


def generate_conclusion_true(document):
    document['data']['title'] = 'Документ для висновку (Document for conclusion, status TRUE)'
    conclusion = {"data": {
                        "conclusion": {
                              "violationType": [
                                    "documentsForm",
                                    "corruptionAwarded"
                              ],
                              "description": "Ashes, ashes, we all fall down 1112222222",
                              "stringsAttached": "Pocket full of posies",
                              "auditFinding": "Ring around the rosies",
                              "violationOccurred": True,
                              "documents": [document['data']]
                            }
                        }
                  }
    return conclusion


def generate_conclusion_false():
    conclusion = {"data": {
                        "conclusion": {
                          "violationOccurred": False,
                        }
                      }
                  }
    return conclusion


def generate_json_for_post(document):
    document['data']['title'] = 'Документ для пояснення (Document for post)'
    post = {"data": {
                    "title": "Lorem ipsum",
                    "description": "Lorem ipsum dolor sit amet.",
                    "documents": [document['data']]
                  }
            }
    return post
