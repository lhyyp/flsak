from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint("web_html", __name__)


@html.route("/<re('.*'):file_name>")
def get_html(file_name):
    if not file_name:
        file_name = "index.html"
    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    # csrf_token = csrf.generate_csrf()
    # resp = make_response(current_app.send_static_file(file_name))
    # resp.set_cookie("csrf_token", csrf_token)
    return current_app.send_static_file(file_name)
