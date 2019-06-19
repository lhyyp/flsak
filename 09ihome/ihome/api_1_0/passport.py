from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
import re
from sqlalchemy.exc import IntegrityError
from ihome.models import User


@api.route("/users", methods=["POST"])
def register():
    """
    注册
    请求参数：手机号、短息验证码、密码
    参数格式：json
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", str(mobile)):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 从redis获取短信验证码，并对比
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as s:
        current_app.logger.error(s)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断短信验证码是否失效
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")
    # 删除短信验证码，防止用户使用一个验证码验证多次
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as s:
        current_app.logger.error(s)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断用户填写短信验证码的正确性
    temp = real_sms_code.decode()
    if temp != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 判断用户手机号是否注册
    user = User(name=mobile, mobile=mobile, password_hash=password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as s:
        # 数据库错误回滚
        db.session.rollback()
        current_app.logger.error(s)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as s:
        # 数据库错误回滚
        db.session.rollback()
        current_app.logger.error(s)
        return jsonify(errno=RET.DATAERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/session", methods=["get"])
def setSession():
    session["name"] = "李白"
    return "setsession"


@api.route("/getsession", methods=["get"])
def getSession():
    name = session.get("name")
    return "setsession %s" % name
