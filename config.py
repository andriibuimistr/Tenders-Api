# -*- coding: utf-8 -*-
import os
from datetime import datetime

import pytz

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DOCS_DIR = os.path.join(ROOT_DIR, 'uploads', 'reports')
kiev_now = str(datetime.now(pytz.timezone('Europe/Kiev')))[26:]
