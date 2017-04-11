#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response, render_template, current_app, \
     session, url_for, redirect
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask_login import login_user, logout_user, \
     login_required, current_user
from datetime import timedelta
from flask_cors import CORS
from . import api
from .. import db

# login lib
from ..decorators import admin_required, permission_required
from ..models import Permission, Role, User, Post

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

@api.route('/post', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_articles():
    if request.method == 'POST':
        body = request.form.get('body')
        title = request.form.get('title')
        author = current_user._get_current_object()
        post = Post(body=body, author=author, title=title)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('base.base_index'))
    else:
        return render_template('post.html')

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
        return 'Unknown Method'

if __name__ == '__main__':
    api.run(debug=True, host='127.0.0.1', port=8000)
