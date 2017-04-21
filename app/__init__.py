from flask import Flask
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from config import config

app = Flask(__name__)
moment=Moment()
db=MongoEngine()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    moment.init_app(app)
    db.init_app(app)

    return app