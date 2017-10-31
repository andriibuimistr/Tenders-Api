# -*- coding: utf-8 -*-
import json

import variables
# enter number of lots from console + validator
from variables import number_of_lots, number_of_items


# generate list of id for lots
def list_of_id():
    list_of_lot_id = []
    for x in range(number_of_lots):
        list_of_lot_id.append(variables.lot_id_generator())
    return list_of_lot_id
list_of_id = list_of_id()


# generate list of lots
def list_of_lots():
    list_of_lots_for_tender = []
    for i in range(number_of_lots):
        lot_id = list_of_id[i]
        one_lot = json.loads(u"{}{}{}{}{}{}{}{}{}{}{}".format(
            '{"id": "', lot_id, '"', variables.title_for_lot(), variables.lot_description(), variables.title_en,
            variables.lot_description_en, variables.lot_guarantee, variables.lot_value, variables.minimal_step(), '}'))
        list_of_lots_for_tender.append(one_lot)
    list_of_lots_for_tender = json.dumps(list_of_lots_for_tender)
    lots_list = u"{}{}{}".format(variables.lots_m, list_of_lots_for_tender, variables.lots_close)
    return lots_list


# generate list of items for lots
def list_of_items_for_lots():
    list_of_items = []
    for i in range(number_of_lots):
        related_lot_id = list_of_id[i]
        item = json.loads(u"{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(
            '{ "relatedLot": ', '"', related_lot_id, '"', variables.description_of_item()[i], variables.classification,
            variables.additionalClassifications, variables.description_en(), variables.delivery_address_block(),
            variables.deliveryDate, variables.item_id_generator(), variables.unit(), variables.quantity, "}"))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(variables.items_m, list_of_items)
    return items_list


# generate list of items for tender
def list_of_items_for_tender():
    list_of_items = []
    for i in range(number_of_items):
        item = json.loads(u"{}{}{}{}{}{}{}{}{}{}{}".format(
            '{', variables.description_of_item()[i], variables.classification,
            variables.additionalClassifications, variables.description_en(), variables.delivery_address_block(),
            variables.deliveryDate, variables.item_id_generator(), variables.unit(), variables.quantity, "}"))
        list_of_items.append(item)
    list_of_items = json.dumps(list_of_items)
    items_list = u"{}{}".format(variables.items_m, list_of_items)
    return items_list
