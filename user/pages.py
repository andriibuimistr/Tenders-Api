# -*- coding: utf-8 -*-
import core
from flask import render_template


class UserPages:

    def __init__(self, session):
        self.session = session

    def page_preferences(self):  # generate page with list of platforms for admin
        content = render_template('user/preferences.html', languages=core.get_list_of_languages(), user_language=self.session['language'])
        return render_template('index.html', content=content)
