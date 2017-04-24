# -*- coding:utf-8 -*-
"""
    rest_views
    ~~~~~~~~~~~~~~~~~~~

    provide rest api for client.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from . import rest_api
from flask import request, Response, abort
from ..models import User, Role
import json
from ..sqllib import DataBaseClient
from ..libs.jsonlib import json_response
from werkzeug.security import generate_password_hash, check_password_hash


@rest_api.route('/users')
def rest_index():
    db = DataBaseClient()
    sql = "select email from users"
    n = db.execute(sql)
    ret = db.fetchall()
    return json_response(ret)


@rest_api.route('/user/register', methods=['POST'])
def rest_register_user():
    email = request.json.get('email', None)
    name = request.json.get('username', None)
    password = request.json.get('password', None)
    confirm_password = request.json.get('confirm_password', None)

    # check incoming params
    if None in (name, email, password, confirm_password):
        return json_response({"result":0, "reason":"params may be wrong"})
    if password != confirm_password:
        return json_response({"request":request.json, "result":0, "reason":"password not match"})
    if len(password) < 6:
        return json_response({"result":0, "reason":"password too short"})

    password_hash = generate_password_hash(password)

    try:
        sql = "insert into users(name, email, passwd_hash, role_id) values('%s','%s','%s',1)" % \
            (str(name), str(email), password_hash)
        db = DataBaseClient()
        n = db.execute(sql)
        if n is 0:
            result = 0
        else:
            result = 1
        reason = ''
    except Exception, exp:
        result = 0
        reason = str(exp)
    return json_response({"result":result, "reason":reason})