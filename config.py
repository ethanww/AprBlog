import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it is my first blog'
    SITE_WIDTH = 800

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS= {
        'db': 'AprBlog',
        'host': '127.0.0.1',
        'port': 27017
    }

class ProductionConfig(Config):
    pass

config={
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}