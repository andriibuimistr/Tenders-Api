# -*- coding: utf-8 -*-
from tenders.tender_additional_data import documents_above_procedures, documents_above_non_financial, documents_above_non_confidential
import requests
import os
import json
from key import auth_key, auth_key_ds





sandbox = 1
if sandbox == 2:
    ds_host = 'https://upload.docs-sandbox.prozorro.openprocurement.net/upload'
    host = 'https://api-sandbox.prozorro.openprocurement.net'
    api_version = 'dev'
else:
    ds_host = 'https://upload.docs-sandbox.openprocurement.org/upload'
    host = 'https://lb.api-sandbox.openprocurement.org'
    api_version = '2.4'



path = os.getcwd()  # path to file for upload
doc_host = host
doc_api_version = api_version


file_for_upload = open('{}{}doc.pdf'.format(path, os.sep), 'rb').read()
filename = 'doc.pdf'
document_data = "----------------------------1507111922.4992\nContent-Disposition: form-data;" \
          "name=\"file\"; filename=\"{}\"\nContent-Type: application/pdf\n\n{}\n" \
                "----------------------------1507111922.4992--".format(filename, file_for_upload)


headers_add_document = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "multipart/form-data; boundary=--------------------------1507111922.4992",
    'cache-control': "no-cache",
    }

headers_patch_document = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "application/json",
    'cache-control': "no-cache",
    }


headers_add_document_ds = {
    'authorization': "Basic {}".format(auth_key_ds),
    'content-type': "multipart/form-data; boundary=--------------------------1507111922.4992",
    'cache-control': "no-cache",
    }

headers_patch_document_ds = {
    'authorization': "Basic {}".format(auth_key),
    'content-type': "application/json",
    'cache-control': "no-cache",
    }


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


# upload document to document service
def upload_documents_to_ds():
    try:
        s = requests.Session()
        s.request("GET", "{}".format(doc_host))
        r = requests.Request('POST',
                             "{}".format(
                                 ds_host),
                             data=document_data,
                             headers=headers_add_document_ds,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Uploading documentation:")
        if resp.status_code == 200:
            print("       status code:  {}".format(resp.status_code))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return 0, resp, resp.status_code
    except Exception as e:
        return 1, e


# upload document from ds to tender
def patch_tender_documents_from_ds(type_for_doc, name_for_doc, added_tender_doc, t_id_long, t_token, lot_id, doc_of):
    patch_bid_json = json.loads(added_tender_doc.content)
    if type_for_doc != 0:
        patch_bid_json['data']['documentType'] = type_for_doc
    patch_bid_json['data']['title'] = name_for_doc
    if doc_of == 'lot':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'lot'
    elif doc_of == 'item':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'item'
    else:
        patch_bid_json['data']['documentOf'] = 'tender'
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
        r = requests.Request('POST',
                             "{}/api/{}/tenders/{}/documents?acc_token={}".format(
                                 doc_host, doc_api_version, t_id_long, t_token),
                             data=json.dumps(patch_bid_json),
                             headers=headers_patch_document_ds,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}'.format("Patching documentation: ", name_for_doc))
        if resp.status_code == 201:
            print("       status code:  {}".format(resp.status_code))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return 0, resp, resp.status_code
    except Exception as e:
        return 1, e


# upload document from ds to bid
def patch_bid_documents_from_ds(
        type_for_doc, name_for_doc, added_tender_doc, t_id_long, bid_id, bid_token, lot_id, doc_of, procurement_method):

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
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
        r = requests.Request('POST',
                             "{}/api/{}/tenders/{}/bids/{}/{}?acc_token={}".format(
                                 doc_host, doc_api_version, t_id_long, bid_id, doc_type_url, bid_token),
                             data=json.dumps(patch_bid_json),
                             headers=headers_patch_document_ds,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}'.format("Patching documentation: ", name_for_doc))
        if resp.status_code == 201:
            print("       status code:  {}".format(resp.status_code))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return 0, resp, resp.status_code
    except Exception as e:
        return 1, e


# add documents to tender ds
def add_documents_to_tender_ds(tender_id_long, tender_token, list_of_id_lots):
    doc_publish_info = []
    for doc_type in tender_documents_type:  # add one document for every document type
        doc_type_name = tender_documents_type[doc_type]
        added_tender_document = upload_documents_to_ds()
        if added_tender_document[0] == 1:
            doc_resp_json = {"upload_document": {"status": "error", "description": str(added_tender_document[1])},
                             "document_name": doc_type_name}
            doc_publish_info.append(doc_resp_json)
        else:
            doc_resp_json = {"upload_document": {"status_code": added_tender_document[2]},
                             "document_name": doc_type_name}
            patch_document_ds = patch_tender_documents_from_ds(doc_type, doc_type_name, added_tender_document[1],
                                                               tender_id_long, tender_token, 0, 'tender')
            if patch_document_ds[0] == 1:
                doc_resp_json["patch_document"] = {"status": "error", "description": str(patch_document_ds[1])}
            else:
                document_id = json.loads(patch_document_ds[1].content)['data']['id']
                doc_resp_json["patch_document"] = {"status_code": patch_document_ds[2], "id": document_id}
            doc_publish_info.append(doc_resp_json)

    lot_number = 0
    for lot in range(len(list_of_id_lots)):
        lot_number += 1
        lot_id = list_of_id_lots[lot]
        for doc_type in tender_documents_type:  # add one document for every document type
            doc_type_name = '{}{}{}'.format(tender_documents_type[doc_type], ' Лот ', lot_number)
            added_tender_document = upload_documents_to_ds()
            if added_tender_document[0] == 1:
                doc_resp_json = {"upload_document": {"status": "error", "description": str(added_tender_document[1])},
                                 "document_name": doc_type_name}
                doc_publish_info.append(doc_resp_json)
            else:
                doc_resp_json = {"upload_document": {"status_code": added_tender_document[2]},
                                 "document_name": doc_type_name}
                patch_document_ds = patch_tender_documents_from_ds(doc_type, doc_type_name, added_tender_document[1],
                                                                   tender_id_long, tender_token, lot_id, 'lot')
                if patch_document_ds[0] == 1:
                    doc_resp_json["patch_document"] = {"status": "error", "description": str(patch_document_ds[1])}
                else:
                    document_id = json.loads(patch_document_ds[1].content)['data']['id']
                    doc_resp_json["patch_document"] = {"status_code": patch_document_ds[2], "id": document_id}
                doc_publish_info.append(doc_resp_json)
    return doc_publish_info


def add_documents_to_bid_ds(tender_id_long, bid_id, bid_token, procurement_method):
    doc_publish_info = []
    bid_document_types = docs_list_for_bid(procurement_method)
    for doc_type in bid_document_types:  # add one document for every document type
        doc_type_name = bid_document_types[doc_type]
        added_bid_document = upload_documents_to_ds()
        if added_bid_document[0] == 1:
            doc_resp_json = {"upload_document": {"status": "error", "description": str(added_bid_document[1])},
                             "document_name": doc_type_name}
            doc_publish_info.append(doc_resp_json)
        else:
            doc_resp_json = {"upload_document": {"status_code": added_bid_document[2]},
                             "document_name": doc_type_name}
            patch_document_ds = patch_bid_documents_from_ds(doc_type, doc_type_name, added_bid_document[1],
                                                            tender_id_long, bid_id, bid_token, 0, 'tender',
                                                            procurement_method)
            if patch_document_ds[0] == 1:
                doc_resp_json["patch_document"] = {"status": "error", "description": str(patch_document_ds[1])}
            else:
                document_id = json.loads(patch_document_ds[1].content)['data']['id']
                doc_resp_json["patch_document"] = {"status_code": patch_document_ds[2], "id": document_id}
            doc_publish_info.append(doc_resp_json)
    return doc_publish_info











'''# upload document to tender
def upload_documents_to_tender(t_id_long, t_token):
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
        r = requests.Request('POST',
                             "{}/api/{}/tenders/{}/documents?acc_token={}".format(
                                 doc_host, doc_api_version, t_id_long, t_token),
                             data=document_data,
                             headers=headers_add_document,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Uploading documentation:")
        if resp.status_code == 201:
            print("       status code:  {}".format(resp.status_code))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return 0, resp, resp.status_code
    except Exception as e:
        return 1, e


# patch document of tender
def patch_document_of_tender(type_for_doc, name_for_doc, added_tender_doc, t_id_long, doc_id, t_token, lot_id, doc_of):
    patch_bid_json = json.loads(added_tender_doc.content)
    if type_for_doc != 0:
        patch_bid_json['data']['documentType'] = type_for_doc
    patch_bid_json['data']['title'] = name_for_doc
    if doc_of == 'lot':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'lot'
    elif doc_of == 'item':
        patch_bid_json['data']['relatedItem'] = lot_id
        patch_bid_json['data']['documentOf'] = 'item'
    else:
        patch_bid_json['data']['documentOf'] = 'tender'
    try:
        s = requests.Session()
        s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
        r = requests.Request('PATCH',
                             "{}/api/{}/tenders/{}/documents/{}?acc_token={}".format(
                                 doc_host, doc_api_version, t_id_long, doc_id, t_token),
                             data=json.dumps(patch_bid_json),
                             headers=headers_patch_document,
                             cookies=requests.utils.dict_from_cookiejar(s.cookies))

        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}'.format("Patching documentation: ", name_for_doc))
        if resp.status_code == 200:
            print("       status code:  {}".format(resp.status_code))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return 0, resp, resp.status_code
    except Exception as e:
        return 1, e


# add documents to tender
def add_documents_to_tender(tender_id_long, tender_token, list_of_id_lots):
    doc_publish_info = []
    for doc_type in tender_documents_type:  # add one document for every document type
        doc_type_name = tender_documents_type[doc_type]
        added_tender_document = upload_documents_to_tender(tender_id_long, tender_token)
        if added_tender_document[0] == 1:
            doc_resp_json = {"status": "error", "description": str(added_tender_document[1]),
                             "document name": doc_type_name}
            doc_publish_info.append(doc_resp_json)
        else:
            document_id = json.loads(added_tender_document[1].content)['data']['id']
            doc_resp_json = {"id": document_id, "upload document": {"status code": added_tender_document[2]}}
            patch_document = patch_document_of_tender(doc_type, doc_type_name, added_tender_document[1], tender_id_long,
                                                      document_id, tender_token, 0, 'tender')
            if patch_document[0] == 1:
                doc_resp_json["patch document"] = {"status": "error", "description": str(patch_document[1])}
            else:
                doc_resp_json["patch document"] = {"status code": patch_document[2], "name": doc_type_name}
            doc_publish_info.append(doc_resp_json)

    lot_number = 0
    for lot in range(len(list_of_id_lots)):
        lot_number += 1
        lot_id = list_of_id_lots[lot]
        for doc_type in tender_documents_type:  # add one document for every document type
            doc_type_name = '{}{}{}'.format(tender_documents_type[doc_type], ' Лот ', lot_number)
            added_tender_document = upload_documents_to_tender(tender_id_long, tender_token)
            if added_tender_document[0] == 1:
                doc_resp_json = {"status": "error", "description": str(added_tender_document[1]),
                                 "document name": doc_type_name}
                doc_publish_info.append(doc_resp_json)
            else:
                document_id = json.loads(added_tender_document[1].content)['data']['id']
                doc_resp_json = {"id": document_id, "upload document": {"status code": added_tender_document[2]}}
                patch_document = patch_document_of_tender(doc_type, doc_type_name, added_tender_document[1],
                                                          tender_id_long, document_id, tender_token, lot_id, 'lot')
                if patch_document[0] == 1:
                    doc_resp_json["patch document"] = {"status": "error", "description": str(patch_document[1])}
                else:
                    doc_resp_json["patch document"] = {"status code": patch_document[2], "name": doc_type_name}
                doc_publish_info.append(doc_resp_json)
    return doc_publish_info'''
