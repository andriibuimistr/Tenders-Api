from flask import render_template
from tools.additional_data import list_of_cdb_for_json_viewer


class Pages:

    def __init__(self, user_role_id):
        self.user_role_id = user_role_id

    def page_json_viewer(self):
        return render_template('tools/json-viewer.html', user_role_id=self.user_role_id, api_versions=list_of_cdb_for_json_viewer)
