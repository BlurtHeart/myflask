# -*- coding:utf-8 -*-
"""
    rest_views
    ~~~~~~~~~~~~~~~~~~~

    provide rest api for client.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from . import rest_api
from flask import request, Response
from ..models import User, Role
import json
from ..sqllib import DataBaseClient
from ..libs.jsonlib import json_response


@rest_api.route('/users')
def rest_index():
    db = DataBaseClient()
    sql = "select email from users"
    n = db.execute(sql)
    ret = db.fetchall()
    return json_response(ret)