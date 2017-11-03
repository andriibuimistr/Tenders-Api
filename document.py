# -*- coding: utf-8 -*-
import requests
import os
import json
import sys
from key import auth_key

path = os.getcwd()
doc_host = 'https://lb.api-sandbox.openprocurement.org'
doc_api_version = '2.4'

'''tender_id_long = '38ead6d4155f48a8b3321ee39b8b1e71'
tender_token = 'e6cf1aca507d4a4b95cea8dfef68aa26'''''


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


def upload_documents_to_tender(t_id_long, t_token):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
    r = requests.Request('POST',
                         "{}/api/{}/tenders/{}/documents?acc_token={}".format(
                             doc_host, doc_api_version, t_id_long, t_token),
                         data=document_data,
                         headers=headers_add_document,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print("Uploading documentation:")
        if resp.status_code == 201:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return resp
    except:
        sys.exit("Error")


def patch_document_of_tender(type_for_doc, name_for_doc, added_tender_doc, t_id_long, doc_id, t_token):
    s = requests.Session()
    s.request("GET", "{}/api/{}/tenders".format(doc_host, doc_api_version))
    patch_bid_json = json.loads(added_tender_doc.content)
    if type_for_doc != 0:
        patch_bid_json['data']['documentType'] = type_for_doc
    patch_bid_json['data']['title'] = name_for_doc
    r = requests.Request('PATCH',
                         "{}/api/{}/tenders/{}/documents/{}?acc_token={}".format(
                             doc_host, doc_api_version, t_id_long, doc_id, t_token),
                         data=json.dumps(patch_bid_json),
                         headers=headers_patch_document,
                         cookies=requests.utils.dict_from_cookiejar(s.cookies))
    try:
        prepped = s.prepare_request(r)
        resp = s.send(prepped)
        print('{}{}'.format("Patching documentation: ", name_for_doc))
        if resp.status_code == 201:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
            print("       headers:           {}".format(resp.headers))
        else:
            print("       status code:  {}".format(resp.status_code))
            print("       response content:  {}".format(resp.content))
        return resp
    except:
        sys.exit("Error")


def add_documents_to_tender(tender_id_long, tender_token):
    tender_documents_type = {'technicalSpecifications': 'Технічний опис предмету закупівлі',
                             'eligibilityCriteria': 'Кваліфікаційні критерії', 'contractProforma': 'Проект договору',
                             'biddingDocuments': 'Тендерна документація'}
    for doc_type in tender_documents_type:
        doc_type_name = tender_documents_type[doc_type]

        added_tender_document = upload_documents_to_tender(tender_id_long, tender_token)
        document_id = json.loads(added_tender_document.content)['data']['id']
        patch_document_of_tender(doc_type, doc_type_name, added_tender_document, tender_id_long,
                                 document_id, tender_token)
    # Add "Інші"
    added_tender_document = upload_documents_to_tender(tender_id_long, tender_token)
    document_id = json.loads(added_tender_document.content)['data']['id']
    patch_document_of_tender(0, "Інші", added_tender_document, tender_id_long,
                             document_id, tender_token)
