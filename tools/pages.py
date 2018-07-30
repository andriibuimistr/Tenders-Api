from flask import render_template
from tools.additional_data import list_of_cdb_for_json_viewer


class Pages:

    def __init__(self):
        pass

    @staticmethod
    def page_json_viewer():
        content = render_template('tools/json-viewer.html', api_versions=list_of_cdb_for_json_viewer)
        return render_template('index.html', content=content, disable_sidebar=True)
