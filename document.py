# -*- coding: utf-8 -*-
from tenders.tender_additional_data import *
import json
from cdb_requests import TenderRequests
from random import choice
from config import ROOT_DIR

sign_name = 'sign.p7s'


def document_data(filename=False):
    if not filename:
        filename = 'doc.pdf'
    file_for_upload = open('{}/{}'.format(ROOT_DIR, 'doc.pdf'), 'rb').read()
    data = "----------------------------1507111922.4992\nContent-Disposition: form-data;" \
           "name=\"file\"; filename=\"{}\"\nContent-Type: application/pdf\n\n{}\n" \
           "----------------------------1507111922.4992--".format(filename, file_for_upload)
    return data


tender_documents_type = {'technicalSpecifications': 'Технічний опис предмету закупівлі',
                         'eligibilityCriteria': 'Кваліфікаційні критерії', 'contractProforma': 'Проект договору',
                         'biddingDocuments': 'Тендерна документація', 0: 'Інші'}


def docs_list_for_bid(procurement_method):
    if procurement_method in documents_above_procedures:  # EU procedures+defense
        bid_document_types = {'technicalSpecifications': 'Технічний опис предмету закупівлі',
                              'qualificationDocuments': 'Документи, що підтверджують кваліфікацію',
                              'eligibilityDocuments': 'Документи, що підтверджують відповідність',
                              'commercialProposal': 'Цінова пропозиція', 'billOfQuantity': 'Кошторис'}
    else:
        bid_document_types = []
    return bid_document_types


financial_documents = ['commercialProposal', 'billOfQuantity']


# upload document from ds to tender
def patch_tender_documents_from_ds(type_for_doc, name_for_doc, added_tender_doc, t_id_long, t_token, lot_id, doc_of, ds):
    add_document_json = json.loads(added_tender_doc.content)
    if type_for_doc != 0:
        add_document_json['data']['documentType'] = type_for_doc
    add_document_json['data']['title'] = name_for_doc
    if doc_of == 'lot':
        add_document_json['data']['relatedItem'] = lot_id
        add_document_json['data']['documentOf'] = 'lot'
    elif doc_of == 'item':
        add_document_json['data']['relatedItem'] = lot_id
        add_document_json['data']['documentOf'] = 'item'
    else:
        add_document_json['data']['documentOf'] = 'tender'
    ds.add_document_from_ds_to_tender(t_id_long, t_token, add_document_json, 'Add document from DS to tender - {}'.format(name_for_doc))


# upload document from ds to bid
def patch_bid_documents_from_ds(type_for_doc, name_for_doc, added_tender_doc, t_id_long, bid_id, bid_token, lot_id, doc_of, procurement_method, ds):
    patch_bid_json = json.loads(added_tender_doc.content)
    patch_bid_json['data']['documentType'] = type_for_doc
    patch_bid_json['data']['title'] = name_for_doc

    if type_for_doc == 'technicalSpecifications' and procurement_method not in documents_above_non_confidential:
        patch_bid_json['data']['confidentialityRationale'] = "Only our company sells badgers with pink hair."
        patch_bid_json['data']['confidentiality'] = "buyerOnly"
        print '                    Confidential document!!!'

    if doc_of == 'lot':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'lot'
    elif doc_of == 'item':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'item'
    else:
        patch_bid_json['data']['documentOf'] = 'tender'

    if type_for_doc in financial_documents and procurement_method not in documents_above_non_financial:
        doc_type_url = 'financial_documents'  # upload financial documents
        print '                    Financial document!!!'
    else:
        doc_type_url = 'documents'
    ds.add_document_from_ds_to_tender_bid(t_id_long, bid_id, doc_type_url, bid_token, patch_bid_json, 'Add document from DS to bid - {}'.format(name_for_doc))


def add_documents_to_tender(tender_id_long, tender_token, list_of_id_lots, api_version):
    doc_publish_info = []
    ds = TenderRequests(api_version)
    for doc_type in tender_documents_type:  # add one document for every document type
        doc_type_name = tender_documents_type[doc_type]
        added_tender_document = ds.add_tender_document_to_ds(document_data())
        patch_tender_documents_from_ds(doc_type, doc_type_name, added_tender_document, tender_id_long, tender_token, 0, 'tender', ds)

    lot_number = 0
    for lot in range(len(list_of_id_lots)):
        lot_number += 1
        lot_id = list_of_id_lots[lot]
        for doc_type in tender_documents_type:  # add one document for every document type
            doc_type_name = '{}{}{}'.format(tender_documents_type[doc_type], ' Лот ', lot_number)
            added_tender_document = ds.add_tender_document_to_ds(document_data())
            patch_tender_documents_from_ds(doc_type, doc_type_name, added_tender_document, tender_id_long, tender_token, lot_id, 'lot', ds)

    return doc_publish_info


def add_documents_to_bid_ds(tender_id_long, bid_id, bid_token, procurement_method, api_version):
    ds = TenderRequests(api_version)
    doc_publish_info = []
    bid_document_types = docs_list_for_bid(procurement_method)
    for doc_type in bid_document_types:  # add one document for every document type
        doc_type_name = bid_document_types[doc_type]
        added_bid_document = ds.add_tender_document_to_ds(document_data())
        patch_bid_documents_from_ds(doc_type, doc_type_name, added_bid_document, tender_id_long, bid_id, bid_token, 0, 'tender', procurement_method, ds)
    return doc_publish_info


def add_document_to_entity(tender_id_long, entity_id, tender_token, api_version, entity, qualified=True):
    ds = TenderRequests(api_version)
    document = ds.add_tender_document_to_ds(document_data())
    document = document.json()
    if entity == 'qualifications':
        document['data']['title'] = 'Document for approve qualification'
        document['data']['documentType'] = choice(document_types_for_award)
        if not qualified:
            document['data']['title'] = 'Document for decline qualification'
    elif entity == 'awards':
        document['data']['title'] = 'Document for approve award'
        document['data']['documentType'] = choice(document_types_for_award)
    elif entity == 'contracts':
        document['data']['title'] = 'Document for contract'
        document['data']['documentType'] = choice(document_types_for_contract)
    ds.add_document_from_ds_to_entity(tender_id_long, entity_id, tender_token, document, 'Add document from DS to {} - {}'.format(entity, entity_id), entity)
    sign = ds.add_tender_document_to_ds(document_data(sign_name)).json()
    ds.add_document_from_ds_to_entity(tender_id_long, entity_id, tender_token, sign, 'Add sign from DS to {} - {}'.format(entity, entity_id), entity)


def add_document_to_tender_ds(api_version):
    ds = TenderRequests(api_version)
    document = ds.add_tender_document_to_ds(document_data())
    document = document.json()
    return document
