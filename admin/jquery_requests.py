from variables import Platforms, Users, db
from flask import render_template, abort, jsonify
import validators
import refresh


def add_platform(request):
    if len(request.form['platform-name']) == 0:
        return abort(400, 'Platform name can\'t be empty')
    if len(request.form['platform-url']) == 0:
        return abort(400, 'Platform url can\'t be empty')

    if validators.url(request.form['platform-url']) is not True:
        abort(400, 'URL is invalid')

    if request.form['platform-url'][-1:] == '/':
        platform_url = request.form['platform-url'][:-1]
    else:
        platform_url = request.form['platform-url']

    platforms_url_list = Platforms.query.all()
    list_platform_url = []
    for url in range(len(platforms_url_list)):
        list_platform_url.append(platforms_url_list[url].platform_url)
    if platform_url in list_platform_url:
        abort(422, 'URL exists in database')

    platform_to_sql = Platforms(None, request.form['platform-name'], platform_url, int(request.form['platform_role']))
    db.session.add(platform_to_sql)
    last_id = Platforms.query.order_by(Platforms.id.desc()).first().id
    newly_added_platform_data = Platforms.query.filter_by(id=last_id)
    db.session.commit()
    db.session.remove()
    return render_template('includes/newly_added_platform_info.inc.html', platform=newly_added_platform_data, platform_roles=refresh.get_list_of_platform_roles())


def add_user(request):
    new_user_data = request.form
    if len(request.form['user-name']) < 4:
        return abort(400, 'User name length can\'t be less than 4')
    if ' ' in request.form['user-name']:
        return abort(422, 'U can\'t use spaces in username')
    if len(request.form['user-password']) < 4:
        return abort(400, 'User password length can\'t be less than 4')
    if ' ' in request.form['user-password']:
        return abort(422, 'U can\'t use spaces in password')
    all_users = refresh.get_list_of_users()
    list_login = []
    for x in range(len(all_users)):
        list_login.append(all_users[x].user_login)
    if request.form['user-name'] in list_login:
        return abort(422, 'We have this login yet')

    user_to_sql = Users(None, new_user_data['user-name'], new_user_data['user-password'], new_user_data['user_role'], int(new_user_data['user_status']), None)
    db.session.add(user_to_sql)
    last_id = Users.query.order_by(Users.id.desc()).first().id
    newly_added_user_data = Users.query.filter_by(id=last_id)
    db.session.commit()
    db.session.remove()
    return render_template('includes/newly_added_user_info.inc.html', user=newly_added_user_data, user_roles=refresh.get_list_of_user_roles())


def delete_platform(platform_id):
    existing_platforms_id = []
    list_of_platforms_id_db = refresh.get_list_of_platforms(False)
    for x in range(len(list_of_platforms_id_db)):
        existing_platforms_id.append(str(list_of_platforms_id_db[x].id))
    if platform_id not in existing_platforms_id:
        return abort(404, 'Platform does not exist')

    Platforms.query.filter_by(id=platform_id).delete()
    db.session.commit()
    db.session.remove()
    return jsonify({"status": "Success"}), 200

