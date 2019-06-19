from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store, constants, db
from flask import current_app, jsonify, make_response, request
from ihome.models import User
import random
import ihome.libs.zhenzismsclient as smsclient


@api.route("/image_code/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return: 正常返回图片 异常：返回json
    """
    # 1、生产验证码图片
    # 名字，真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()
    # 2、将验证码真实值保存redis
    try:
        # 记录名字    有效期   记录值
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as s:
        current_app.logger.error(s)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码错误")

    # 返回值
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


@api.route("/sms_code/<re(r'1\d{10}'):mobile>")
def get_sms_code(mobile):
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 从redis取出图片验证码，并对比
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)

    except Exception as s:
        current_app.logger.error(s)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")
    # 图片验证码失效
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # 删除图片验证码，防止用户使用一个验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as s:
        current_app.logger.error(s)
    temp = real_image_code.decode()

    if temp.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 判断手机号在60s内有没有记录，如果有，则认为用户频繁操作
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as s:
        current_app.logger.error(s)
    else:
        if send_flag is not None:
            # 表示该手机号60s内有记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60s后重试")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as s:
        current_app.logger.error(s)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 如果手机号码不存在，则生成验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 短信验证码保存redis
    try:
        # 记录名字    有效期   记录值
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存这个手机号码的记录，防止用户在60s内再次触发发短信操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_REDIS_EXPIRES, 1)
    except Exception as s:
        current_app.logger.error(s)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

    # 发送短信
    # client = smsclient.ZhenziSmsClient(constants.APIURL, constants.APPID, constants.APPSECRET)
    # result = client.send(mobile, '您的验证码为%s' % sms_code)
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="您的验证码为%s" % sms_code)
