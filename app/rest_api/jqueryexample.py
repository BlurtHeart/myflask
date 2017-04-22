# -*- coding:utf-8 -*-
"""
    jqueryexample
    ~~~~~~~~~~~~~~~~~~~

    provide a jquery example of using the rest apis.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from . import rest_api
from flask import render_template


@rest_api.route('/jquery/')
def jquery_index():
    return render_template('jquery/index.html')