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

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@login_manager.user_loader
def load_user(user_id):
    name = ''
    for each in user_info:
        id = int(user_id)
        if id == each['id']:
            name = each['name']
            break
    user = User(user_id, name)
    return user

@login_manager.unauthorized_handler
def unauthorized():
    print 'client unauthorized'
    print 'login session:', session
    return 'unauthorized'

@login_required
@admin_required
@app.route('/admin')
def for_admins_only():
    return 'For Administrators'

@app.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For Comment Moderators'

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print 'post login session:', session
        if request.json == None:
            name = request.form.get('username')
            passwd = request.form.get('passwd')
        else:
            print 'request:', request.json
            name = request.json.get('username')
            passwd = request.json.get('passwd')
        user_id = 0
        for each in user_info:
            if name == each['name']:
                user_id = each['id']
        user = User(user_id, name)
        login_user(user)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        return 'login ok'
    else:
        print 'get login session:', session
        return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    print 'get logout session:', session
    logout_user()
    return 'logout.'

@app.route('/secret')
@login_required
def secret():
    print 'get secret session:', session
    return 'secret'

@login_required
def get_test():
    return 'get test'

@login_required
def post_test():
    return 'post test'

@app.route('/test', methods=['GET', 'POST'])
def test():
    print request.headers
    print request.path
    if request.method == 'GET':
        return get_test()
    elif request.method == 'POST':
        return post_test()
    else:
        return 'Unkown Method'

@app.route('/')
def index():
    return 'Home Page'

@app.route('/about')
def about():
    return 'About Page'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
