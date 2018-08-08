import core
from flask import render_template, render_template_string


class AdminPages:

    def __init__(self):
        pass

    @staticmethod
    def page_admin_platforms():  # generate page with list of platforms for admin
        content = render_template('admin/platforms.html', platforms=core.get_list_of_platforms(False),
                                  platform_roles=core.get_list_of_platform_roles())
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_users(session):  # generate page with list of user for admin
        content = render_template('admin/users.html', users=core.get_list_of_users(),
                                  user_roles=core.get_list_of_user_roles(),
                                  super_user_flag=session['super_user'])
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_tenders():  # generate page with list of user for admin
        content = render_template('admin/tenders.html', tenders=core.get_list_of_tenders())
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_auctions():  # generate page with list of user for admin
        content = render_template('admin/auctions.html', auctions=core.get_list_of_auctions())
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_reports():  # generate page with list of user for admin
        content = render_template('admin/reports.html', report_types=core.get_list_of_report_types(),
                                  report_statuses=core.get_list_of_report_statuses(),
                                  report_priorities=core.get_list_of_report_priorities(),
                                  reports=core.get_list_of_reports())
        return render_template('index.html', content=content)

    @staticmethod
    def page_admin_report_view(report_id):
        report = core.get_report_info(report_id)
        content = render_template('report_view.html', report=report,
                                  report_content=render_template_string(report.content),  # Convert report content to HTML
                                  report_types=core.get_list_of_report_types(),
                                  report_statuses=core.get_list_of_report_statuses(),
                                  report_priorities=core.get_list_of_report_priorities(),
                                  report_documents=core.get_report_documents(report_id),
                                  report_images=core.get_report_images(report_id))
        return render_template('index.html', content=content)
