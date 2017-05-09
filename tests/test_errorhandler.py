# -*- coding:utf-8 -*-
"""
    tests.client
    ~~~~~~~~~~~~~~~~~~~

    Tests Flask Client.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""

from app import create_app, db
from flask import url_for, redirect
from app.models import Role, User
import unittest
import json


class FlaskErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['SERVER_NAME'] = '127.0.0.1:%d' %self.app.config['FLASK_SERVER_PORT']
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_404_json_response(self):
        headers = {'Accept':'application/json'}
        response = self.client.get(path='%s/never-defined/404' %self.app.config['SERVER_NAME'], \
                content_type="application/json", headers=headers)
        try:
            data = json.loads(response.data)
        except ValueError:
            self.fail('response is not a json data!')
        self.assertTrue('error' in data)

    def test_404_html_response(self):
        response = self.client.get(path='%s/never-defined/404' %self.app.config['SERVER_NAME'])
        with self.assertRaises(ValueError):
            data = json.loads(response.data)
