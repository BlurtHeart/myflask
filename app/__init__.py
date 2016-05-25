from flask import Flask
from flask.ext.cors import CORS
from flask.ext.login import LoginManager
from datetime import timedelta
from flask.ext.sqlalchemy import SQLAlchemy

login_manager = LoginManager()
login_manager.session_protection = 'strong'
db = SQLAlchemy()

# create app
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = 'you-will-never-guest-out'
    app.permanent_session_lifetime = timedelta(minutes=1)

    login_manager.init_app(app)
    db.init_app(app)
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    from .base import base
    app.register_blueprint(base)
    return app

# create db
from .sqllib import DataBaseClient
def create_db():
    sql = "create table user_info ( \
    `id` int not null, \
    `username` varchar(20) not null unique, \
    `passwd` varchar(10) not null, \
    `role` int not null, \
    primary key (`id`))"
    db = DataBaseClient(path='data-base.db')
    ret = db.execute(sql)
    if not ret:
        return 0    # failed
    return 1

