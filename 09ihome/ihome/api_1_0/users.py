from . import api
from ihome import db, models
from flask import current_app


@api.route("/")
def index():
    current_app.logger.error("err msg")
    current_app.logger.warn("warn msg")
    current_app.logger.info("info msg")
    current_app.logger.debug("debug msg")
    return "index111 page"
