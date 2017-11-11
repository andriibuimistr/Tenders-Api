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
from flask import Flask, jsonify, request, abort, make_response


app = Flask(__name__)


# ###################### ERRORS ################################
@app.errorhandler(400)
def custom400(error):
    return make_response(jsonify(
        {'error': '400 Bad Request', 'description': error.description}), 400)


@app.errorhandler(422)
def custom422(error):
    return make_response(jsonify(
        {'error': '422 Unprocessable Entity', 'description': error.description}), 422)


@app.errorhandler(404)
def custom404(error):
    return make_response(jsonify(
        {'error': '404 Not Found', 'description': error.description}), 404)
# db = MySQLdb.connect(host="localhost", user="python", passwd="python", db="python_dz")
# cursor = db.cursor()


@app.route('/')
def index():
    return "Main page"
# create tender example
'''data = {
    "data": {
        "procurementMethodType": "aboveThresholdEU",
        "number_of_lots": 2,
        "number_of_items": 3,
        "documents": 0,
        "bids": 3
    }
}'''

# procurement_method = 'aboveThresholdUA'
# number_of_lots = 0
# number_of_items = 2
# add_documents = 0
# number_of_bids = 1


@app.route('/api/tenders', methods=['POST'])
def create_tender_function():
    tc_request = request.json['data']
    if not tc_request or 'procurementMethodType' not in tc_request or 'number_of_lots' not in tc_request \
            or 'number_of_items' not in tc_request or 'documents' not in tc_request \
            or 'number_of_bids' not in tc_request:
        abort(400)

    procurement_method = tc_request["procurementMethodType"]
    number_of_lots = tc_request["number_of_lots"]
    number_of_items = tc_request["number_of_items"]
    add_documents = tc_request["documents"]
    number_of_bids = tc_request["number_of_bids"]

    if type(number_of_lots) != int:
        abort(400, 'Number of lots must be integer')
    elif 0 > number_of_lots or number_of_lots > 10:
        abort(422, 'Number of lots must be between 0 and 10')

    if type(number_of_items) != int:
        abort(400, 'Number of items must be integer')
    elif 1 > number_of_items or number_of_items > 10:
        abort(422, 'Number of items must be between 1 and 10')

    if type(add_documents) != int:
        abort(400, 'Documents must be integer')
    elif 0 > add_documents or add_documents > 1:
        abort(422, 'Documents must be 0 or 1')

    if type(number_of_bids) != int:
        abort(400, 'Number of bids must be integer')
    elif 0 > number_of_bids or number_of_bids > 10:
        abort(422, 'Number of bids must be between 0 and 10')

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
        return jsonify({'data': {
            "tender": [{
                "publish tender": publish_tender_response[1],
                "activate tender": activate_tender[1],
                "add tender to db": add_tender_db
            }],
            "bids": run_create_tender

        }
        })
    elif procurement_method in variables.below_threshold_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    elif procurement_method in variables.limited_procurement:
        print "Error. Данный функционал еще не был разработан :)"
        abort(422, "This procurementMethodType wasn't implemented yet")
    else:
        abort(400, 'Incorrect procurementMethodType')


@app.route('/api/tenders/synchronization', methods=['GET'])
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
