import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "dfjsabvavhaae5353i"
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/ihome"
    # 设置salalchemy自动跟踪数据库库
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # flask-session配置
    SESSION_TYPE = "REDIS"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的id隐藏
    PERMANENT_SESSION_LIFETIME = 86400  # session有效期


class DevelopmentConfig(Config):
    """开发模式配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
