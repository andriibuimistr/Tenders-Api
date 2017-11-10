# -*- coding: utf-8 -*-
import variables
import tender
import document
import bid
import json
import sys
import qualification
import time
import refresh
from flask import Flask, jsonify


app = Flask(__name__)

# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
# cursor = db.cursor()


@app.route('/')
def index():
    return "Main page"


# procurement_method = 'aboveThresholdUA'
# number_of_lots = 0
# number_of_items = 2
# add_documents = 0
# number_of_bids = 1


@app.route('/api/tenders/type/<procurement_method>/lots/<int:number_of_lots>/items/<int:number_of_items>/documents/'
           '<int:add_documents>/bids/<int:number_of_bids>', methods=['POST'])
def create_tender_function(procurement_method, number_of_lots, number_of_items, add_documents, number_of_bids):
    """procurement_method = variables.procurement_method_selector()
    if procurement_method in variables.above_threshold_procurement:
        number_of_lots = variables.number_of_lots()
        if number_of_lots == 0:
            number_of_items = variables.number_of_items()
        else:
            number_of_items = 0
    elif procurement_method in variables.below_threshold_procurement:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    else:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    number_of_bids = bid.number_of_bids()"""
    if procurement_method in variables.above_threshold_procurement:
        list_of_id_lots = tender.list_of_id_for_lots(number_of_lots)  # get list of id for lots
        # select type of tender (with or without lots)
        if number_of_lots == 0:
            json_tender = json.loads(tender.tender(number_of_lots, number_of_items, procurement_method))
        else:
            json_tender = json.loads(tender.tender_with_lots(number_of_lots, number_of_items, list_of_id_lots,
                                                             procurement_method))
        headers_tender = tender.headers_tender(json_tender)  # get headers for publish tender
        publish_tender_response = tender.publish_tender(headers_tender, json_tender)  # publish tender in draft status
        activate_tender = tender.activating_tender(publish_tender_response[0], headers_tender)  # activate tender

        tender_id_long = publish_tender_response[0].headers['Location'].split('/')[-1]
        tender_token = publish_tender_response[0].json()['access']['token']
        tender_status = activate_tender[0].json()['data']['status']

        # add documents to tender
        if add_documents == 1:
            document.add_documents_to_tender(tender_id_long, tender_token)
        # add tender to database
        add_tender_db = tender.tender_to_db(tender_id_long, publish_tender_response[0], tender_token,
                                            procurement_method, tender_status, number_of_lots)
        # tender.add_tender_to_site(tender_id_long, tender_token)
        # bids
        run_create_tender = bid.run_cycle(number_of_bids, number_of_lots, tender_id_long, procurement_method,
                                          list_of_id_lots)
    elif procurement_method in variables.below_threshold_procurement:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    else:
        sys.exit("Error. Данный функционал еще не был разработан :)")
    return jsonify({'data': {
                            "tender": [{
                                "publish tender": publish_tender_response[1],
                                "activate tender": activate_tender[1],
                                "add tender to db": add_tender_db
                            }],
                            "bids": run_create_tender

    }
    })


@app.route('/api/synchronization', methods=['GET'])
def update_list_of_tenders():
    db = variables.database()
    cursor = db.cursor()
    refresh.update_tenders_list(cursor)
    db.commit()
    db.close()
    return jsonify({"status": "success"})


@app.route('/api/tenders', methods=['GET'])
def get_list_of_tenders():
    db = variables.database()
    cursor = db.cursor()
    list_of_tenders = refresh.get_tenders_list(cursor)
    db.commit()
    db.close()
    return jsonify({"data": {"tenders": list_of_tenders}})
# ########################## PREQUALIFICATIONS ###################################


@app.route('/api/tenders/prequalification', methods=['GET'])
def get_list_tenders_prequalification_status():
    db = variables.database()
    cursor = db.cursor()
    list_tenders_preq = refresh.get_tenders_prequalification_status(cursor)
    db.commit()
    db.close()
    list_json = []
    for x in range(len(list_tenders_preq)):
        id_tp = list_tenders_preq[x][0]
        procedure = list_tenders_preq[x][1]
        status = list_tenders_preq[x][2]
        list_json.append({"id": id_tp, "procurementMethodType": procedure, "status": status})
    return jsonify({'data': {"tenders": list_json}})


@app.route('/api/tenders/prequalification/<tender_id_long>', methods=['POST'])
def pass_prequalification(tender_id_long):
    # tender_id_long = raw_input('Tender ID: ')
    db = variables.database()
    cursor = db.cursor()
    tender_token = qualification.get_tender_token(tender_id_long, cursor)  # get tender token
    qualifications = qualification.list_of_qualifications(tender_id_long)  # get list of qualifications for tender
    prequalification_result = qualification.select_my_bids(
        qualifications, tender_id_long, tender_token, cursor)  # approve all my bids
    time.sleep(2)
    finish_prequalification = qualification.finish_prequalification(
        tender_id_long, tender_token)  # submit prequalification protocol
    db.commit()
    db.close()
    return jsonify({'data': {"tenderID": tender_id_long, "prequalifications": prequalification_result,
                             "submit protocol": finish_prequalification}})


# db.close()

if __name__ == '__main__':
    app.run(debug=True)
