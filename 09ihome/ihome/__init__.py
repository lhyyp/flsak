from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_map
import redis
import logging
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
import pymysql
from ihome.utils.commont import ReConverter

pymysql.install_as_MySQLdb()

# 数据库
db = SQLAlchemy()
# 創建redis链接对象
redis_store = None

# 设置日志的记录登记
logging.basicConfig(level=logging.WARNING)
# 创建日志记录器，指明保存路径，每个日志文件最大大小，保存日志文件最大个数
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录格式 、日志等级、输入日志信息文件名行数日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为创建的日志设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局日志工具对象
logging.getLogger().addHandler(file_log_handler)


# 工厂模式
def create_app(config_name):
    """
    创建flask应用对象
    :param config_name: str  配置模式的名字（"develop", "product"）
    :return:
    """
    app = Flask(__name__)
    # 根据配置模式的名字获取配置参数
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用flask-session,将session存到redis中
    Session(app)

    # 为flask提供csrf防护
    # CSRFProtect(app)

    #  为flask添加自定义转换器
    app.url_map.converters["re"] = ReConverter
    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")
    from ihome import web_html
    app.register_blueprint(web_html.html)
    return app
