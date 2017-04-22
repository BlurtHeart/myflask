# -*- coding:utf-8 -*-
"""
    jsonlib
    ~~~~~~~~~~~~~~~~~~~

    provide json structure to flask response.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from flask import Response
import json
from datetime import datetime, date


__all__ = ['json_response']


class CJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def json_response(ret):
    strj = json.dumps(ret, cls=CJSONEncoder)
    return Response(strj, status=200, mimetype='application/json')