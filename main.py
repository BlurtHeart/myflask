#!/usr/bin/env python
from flask import Flask, request, Response, render_template, current_app, \
     session
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask.ext.login import LoginManager, login_user, logout_user, \
     login_required, current_user, UserMixin
from datetime import datetime
from flask.ext.cors import CORS

# login lib
from decorators import admin_required, permission_required
from models import Permission, Role

app = Flask(__name__)
CORS(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'

app.secret_key = 'you-will-never-guest-out'
app.permanent_session_lifetime = timedelta

user_info = [{'id':1,'name':'abc','passwd':'111111','role':Permission.MODERATE_COMMENTS}]
class User(UserMixin):
    role = {'permissions':Permission.MODERATE_COMMENTS}
    def __init__(self, id, name, **kwargs):
        print 'id', id, 'name:', name
        self.id = id
        self.name = name
        
        self.role = {'permissions':Permission.FOLLOW}
        for u in user_info:
            if int(id) == u['id']:
                self.role = {'permissions':u['role']}
                break
        super(User, self).__init__(**kwargs)
    def can(self, permissions):
        return self.role is not None and \
               (self.role['permissions'] &permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

@app.errorhandler(403)
def forbidden_user(error):
    return 'user forbiddent!' + str(error)

@app.route('/')
def index():
    return 'Home Page'

@app.route('/about')
def about():
    return 'About Page'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
