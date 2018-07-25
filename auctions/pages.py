# -*- coding: utf-8 -*-
from flask import render_template
import core
from auction_additional_data import *


class AuctionPages:

    def __init__(self):
        pass

    @staticmethod
    def page_create_auction():
        content = render_template('auctions/create_auction.html', list_of_types=auction_procurement_method_types, cdb_versions=cdb_versions, platforms=core.get_list_of_platforms(2),
                                  statuses=auction_status_to_create, steps=dgf_insider_steps)
        return render_template('index.html', content=content)

    @staticmethod
    def page_auction_bids():
        content = render_template('auctions/auction_bids.html')
        return render_template('index.html', content=content)
