from flask import Flask
from flask.ext.cors import CORS
from flask.ext.login import LoginManager
from datetime import timedelta

login_manager = LoginManager()
login_manager.session_protection = 'strong'

# create app
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = 'you-will-never-guest-out'
    app.permanent_session_lifetime = timedelta(minutes=1)

    login_manager.init_app(app)
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    return app
