# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from faker import Faker
from config import kiev_now
from document import *
from pprint import pprint

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


def generate_decision(cdb, add_documents):
    decision = {"data": {
                    "decision": {
                      "date": decision_date(),
                      "description": fake.text(500).replace('\n', ' '),
                    }
                  }
                }
    if add_documents:
        documents = list()
        for doc in range(5):
            document = add_document_to_tender_ds(cdb)
            document['data']['title'] = 'Документ для рішення про початок моніторингу (Document for decision) - {}'.format(doc + 1)
            documents.append(document['data'])
        decision['data']['decision']['documents'] = documents
    return decision


def generate_conclusion_true(cdb, add_documents):
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
                            }
                        }
                  }
    if add_documents:
        document = add_document_to_tender_ds(cdb)
        document['data']['title'] = 'Документ для висновку. Порушення виявлені (Document for conclusion, status TRUE)'
        conclusion['data']['conclusion']['documents'] = [document['data']]
    return conclusion


def generate_conclusion_false(cdb, add_documents):
    conclusion = {"data": {
                        "conclusion": {
                          "violationOccurred": False,
                        }
                      }
                  }
    if add_documents:
        document = add_document_to_tender_ds(cdb)
        document['data']['title'] = 'Документ для висновку. Порушення не виявлені (Document for conclusion, status FALSE)'
        conclusion['data']['conclusion']['documents'] = [document['data']]
    return conclusion


def generate_json_for_post(cdb, add_documents):
    post = {"data": {
                    "title": fake.text(50).replace('\n', ' '),
                    "description": fake.text(200).replace('\n', ' '),
                  }
            }
    if add_documents:
        document = add_document_to_tender_ds(cdb)
        document['data']['title'] = 'Документ для пояснення (Document for post)'
        post['data']['documents'] = [document['data']]
    return post


def elimination_resolution(cdb, add_documents):

    resolution = {"data": {
                        "eliminationResolution": {
                          "description": fake.text(200).replace('\n', ' '),
                          "resultByType": {
                            "corruptionAwarded": "not_eliminated",
                            "documentsForm": "eliminated"
                          },
                          "result": "partly"
                        }
                      }
                  }
    if add_documents:
        document = add_document_to_tender_ds(cdb)
        document['data']['title'] = 'Документ про Підтвердження факту усунення порушення (Document of eliminationResolution)'
        resolution['data']['eliminationResolution']['documents'] = [document['data']]
    return resolution


def elimination_report(cdb, add_documents):
    report = {"data": {
                "description": "The procurement requirements have been fixed and the changes are attached."
              }
              }
    if add_documents:
        document = add_document_to_tender_ds(cdb)
        document['data']['title'] = 'Документ до Оприлюднення інформації про усунення порушень (Document of eliminationReport)'
        report['data']['documents'] = [document['data']]
    return report


def monitoring_to_cancelled_json():
    data = {"data": {
                    "status": "cancelled",
                    "cancellation": {
                      "description": fake.text(200).replace('\n', ' ')
                    }
                  }
            }
    return data
