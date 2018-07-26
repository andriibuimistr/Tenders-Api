import core
from flask import render_template


class AdminPages:

    def __init__(self):
        pass

    @staticmethod
    def page_admin_platforms():  # generate page with list of platforms for admin
        content = render_template('admin/platforms.html', platforms=core.get_list_of_platforms(False), platform_roles=core.get_list_of_platform_roles())
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_users(session):  # generate page with list of user for admin
        content = render_template('admin/user.html', users=core.get_list_of_users(), user_roles=core.get_list_of_user_roles(),
                                  super_user_flag=session['super_user'])
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_tenders():  # generate page with list of user for admin
        content = render_template('admin/tenders.html', tenders=core.get_list_of_tenders())
        return render_template('index.html', content=content)

