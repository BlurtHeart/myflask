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


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['SERVER_NAME'] = '127.0.0.1:%d' %self.app.config['FLASK_SERVER_PORT']
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('base.base_index'))
        self.assertTrue(b'Stranger' in response.data)

    def test_register_and_login(self):
        response = self.client.post(url_for('base.base_register_user'), data={
                "email":"test@test.com",
                "password":"xxxxxxxx"
            })
        self.assertTrue(response.status_code==302)

        user = User.query.filter_by(email="test@test.com").first()
        self.assertFalse(user is None)

        # login
        response = self.client.post(url_for('base.base_login'), data={
                "email":"test@test.com",
                "passwd":"xxxxxxxx"
            })
        self.assertTrue(response.status_code==302)