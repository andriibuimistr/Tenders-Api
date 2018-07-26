# -*- coding: utf-8 -*-
from core import get_list_of_languages
from flask import abort
from database import db, Users, Languages


def save_user_preferences(data, session):
    lang_id = None
    if 'language' in data:
        languages = get_list_of_languages()
        list_of_language_values = list()
        for lng in range(len(languages)):
            list_of_language_values.append(languages[lng].system_name)
        if data['language'] not in list_of_language_values:
            abort(422, 'Invalid language value')  # replace with template in the future

        lang_id = Languages.query.filter_by(system_name=data['language']).first().id
        session['language'] = data['language']

    Users.query.filter_by(id=session['user_id']).update(dict(user_lang_id=lang_id))

    db.session.commit()
    db.session.remove()
