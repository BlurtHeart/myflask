#!/usr/bin/env python
from flask import Flask, request, Response, render_template, current_app, \
     session
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask.ext.login import login_user, logout_user, \
     login_required 
from datetime import timedelta
from flask.ext.cors import CORS
from . import api
from ..models import User, user_info

# login lib
from ..decorators import admin_required, permission_required
from ..models import Permission, Role

@api.errorhandler(403)
def forbidden_user(error):
    return 'user forbiddent!' + str(error)

@api.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@login_required
@admin_required
@api.route('/admin')
def for_admins_only():
    return 'For Administrators'

@api.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For Comment Moderators'

@api.route('/login', methods=['POST', 'GET'])
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
    
@api.route('/logout')
@login_required
def logout():
    print 'get logout session:', session
    logout_user()
    return 'logout.'

@api.route('/secret')
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

@api.route('/test', methods=['GET', 'POST'])
def test():
    print request.headers
    print request.path
    if request.method == 'GET':
        return get_test()
    elif request.method == 'POST':
        return post_test()
    else:
        return 'Unkown Method'

@api.route('/')
def index():
    return 'Home Page'

@api.route('/about')
def about():
    return 'About Page'

if __name__ == '__main__':
    api.run(debug=True, host='127.0.0.1', port=8000)
