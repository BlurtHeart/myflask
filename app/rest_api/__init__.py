# -*- coding:utf-8 -*-
"""
    __init__
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint

rest_api = Blueprint('rest_api', __name__)

from . import rest_views, authentication
from . import jqueryexample
