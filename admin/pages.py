import refresh
from flask import render_template


class AdminPages:

    def __init__(self, user_role_id):
        self.user_role_id = user_role_id

    def page_admin_platforms(self):  # generate page with list of platforms for admin
        content = render_template('admin/platforms.html', platforms=refresh.get_list_of_platforms(False), platform_roles=refresh.get_list_of_platform_roles())
        return render_template('index.html', user_role_id=self.user_role_id, content=content)

    def page_admin_users(self):  # generate page with list of users for admin
        content = render_template('admin/users.html', users=refresh.get_list_of_users(), user_roles=refresh.get_list_of_user_roles())
        return render_template('index.html', user_role_id=self.user_role_id, content=content)
