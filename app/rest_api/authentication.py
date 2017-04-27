# -*- coding:utf-8 -*-
"""
    authentication
    ~~~~~~~~~~~~~~~~~~~

    provide http basic auth for rest api.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from flask import abort, g, jsonify
from . import rest_api


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.use_token = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.use_token = False
    return user.verify_password(password)


@auth.error_handler
def error_handler():
    abort(400)


@rest_api.route('/token')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.use_token:
        abort(400)
    return jsonify({'token': g.current_user.generate_auth_token(expires_in=3600), 'expires_in': 3600})