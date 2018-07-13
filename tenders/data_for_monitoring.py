# -*- coding: utf-8 -*-
from datetime import timedelta
from tenders.tender_additional_data import *


def decision_date():
    return (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S{}".format(kiev_now))


def generate_monitoring_json(tender_id_long):
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


def generate_decision():
    decision = {"data": {
                    "decision": {
                      "date": decision_date(),
                      "description": "Описание decision"
                    }
                  }
                }
    return decision


def generate_conclusion_true():
    conclusion = {"data": {
                        "conclusion": {
                              "violationType": [
                                    "documentsForm",
                                    "corruptionAwarded"
                              ],
                              "description": "Ashes, ashes, we all fall down 1112222222",
                              "stringsAttached": "Pocket full of posies",
                              "auditFinding": "Ring around the rosies",
                              "violationOccurred": True
                            }
                        }
                  }
    return conclusion


def generate_conclusion_false():
    conclusion = {"data": {
                        "conclusion": {
                          # "relatedParty": "3f193d61e4ca3863a60e29557b338073",
                          "violationOccurred": False
                        }
                      }
                  }
    return conclusion
