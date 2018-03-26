import core
from flask import render_template


class AdminPages:

    def __init__(self, user_role_id):
        self.user_role_id = user_role_id

    def page_admin_platforms(self):  # generate page with list of platforms for admin
        content = render_template('admin/platforms.html', platforms=core.get_list_of_platforms(False), platform_roles=core.get_list_of_platform_roles())
        return render_template('index.html', user_role_id=self.user_role_id, content=content)

    def page_admin_users(self):  # generate page with list of users for admin
        content = render_template('admin/users.html', users=core.get_list_of_users(), user_roles=core.get_list_of_user_roles())
        return render_template('index.html', user_role_id=self.user_role_id, content=content)

    def page_admin_tenders(self):  # generate page with list of users for admin
        content = render_template('admin/tenders.html', tenders=core.get_list_of_tenders())
        return render_template('index.html', user_role_id=self.user_role_id, content=content)

