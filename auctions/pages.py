# -*- coding: utf-8 -*-
from flask import render_template
import refresh
from auction_additional_data import auction_procurement_method_types, cdb_versions, auction_status_to_create


class AuctionPages:

    def __init__(self, user_role_id):
        self.user_role_id = user_role_id

    def page_create_auction(self):
        content = render_template('auctions/create_auction.html', list_of_types=auction_procurement_method_types, cdb_versions=cdb_versions, platforms=refresh.get_list_of_platforms(2),
                                  statuses=auction_status_to_create)
        return render_template('index.html', user_role_id=self.user_role_id, content=content)