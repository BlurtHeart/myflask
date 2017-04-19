# -*- coding: utf-8 -*-
"""
    tests.user
    ~~~~~~~~~~~~~~~~~~~

    Tests User Model.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""

import unittest
from flask import current_app
from app import create_app, db
from app.models import User, AnonymousUser, Permission, Follow, Role
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop() 

    def test_user_insert(self):
        user = User(name='Blurt', email='blurt@test.com', password='111111')
        db.session.add(user)
        db.session.commit()
        query_user = user.query.filter_by(name='Blurt').first()
        self.assertTrue(query_user is not None)
        db.session.delete(user)
        db.session.commit()    

    def test_password_invisible(self):
        user = User(name='Blurt', email='blurt@test.com', password='111111')
        self.assertTrue(user.passwd_hash is not None)
        self.assertFalse(user.passwd_hash == '111111')
        with self.assertRaises(AttributeError):
            password = user.password

    def test_password_verify(self):
        user = User(name='Blurt', email='blurt@test.com', password='111111')
        self.assertTrue(user.verify_password('111111'))
        self.assertFalse(user.verify_password('222222'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.passwd_hash != u2.passwd_hash)

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_confirm_token(self):
        user = User(name='Heart', email='heart@test.com', password='111111')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))
        db.session.delete(user)
        db.session.commit()

    def test_insert_duplicate(self):
        user = User(name='duplicate', email='duplicate@test.com', password='duplicate')
        db.session.add(user)
        db.session.commit()
        with self.assertRaises(IntegrityError):
            user2 = User(name='duplicate2', email='duplicate@test.com', password='xxxxxx')
            db.session.add(user2)
            db.session.commit()
            db.session.delete(user)
            db.session.delete(user2)
            db.session.commit()

    def test_adminstrator(self):
        Role.insert_roles()
        user = User(name='xxxx', email=current_app.config['FLASKY_ADMIN'], password='xxxxx')
        self.assertTrue(user.is_administrator())

    def test_follows(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)