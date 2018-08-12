# -*- coding: utf-8 -*-
from flask import render_template
import core
from .tender_additional_data import *


class TenderPages:

    def __init__(self):
        pass

    @staticmethod
    def page_create_tender():
        content = render_template('tenders/create_tender.html',
                                  list_of_types=list_of_procurement_types,
                                  api_versions=list_of_api_versions,
                                  platforms=core.get_list_of_platforms(1),
                                  statuses=tender_status_list)
        return render_template('index.html', content=content)

    @staticmethod
    def page_create_monitoring():
        content = render_template('tenders/create_monitoring.html',
                                  list_of_types=list_of_procurement_types,
                                  api_versions=list_of_api_versions,
                                  platforms=core.get_list_of_platforms(1),
                                  statuses=monitoring_status_list)
        return render_template('index.html', content=content)

    @staticmethod
    def page_tender_bids():
        content = render_template('tenders/tender_bids.html')
        return render_template('index.html', content=content)
