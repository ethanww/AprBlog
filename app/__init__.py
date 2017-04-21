from flask import Flask
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from config import config
from flask_admin import Admin

moment=Moment()
db=MongoEngine()
admin=Admin()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # app.config['MONGODB_SETTINGS'] = {
    #     'db': 'AprBlog',
    #     'host': '127.0.0.1',
    #     'port': 27017
    # }
    # app.secret_key = 'it is my first blog'

    moment.init_app(app)
    db.init_app(app)
    admin.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app