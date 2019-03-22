# -*- coding:utf-8 -*-
"""
    rest_views
    ~~~~~~~~~~~~~~~~~~~

    provide rest api for client.

    :copyright: (c) 2017 by Blurt Heart.
    :license: BSD, see LICENSE for more details.
"""
from . import rest_api
from flask import request, Response, abort, render_template, url_for, g
from ..models import User, Role, Post, Comment
import json
from ..sqllib import DataBaseClient
from ..libs.jsonlib import json_response
from werkzeug.security import generate_password_hash, check_password_hash
from .authentication import auth
from datetime import datetime


@rest_api.route('/users')
def rest_users():
    db = DataBaseClient()
    sql = "select email from users"
    n = db.execute(sql)
    ret = db.fetchall()
    return json_response(ret)


@rest_api.route('/login', methods=['GET', 'POST'])
def rest_login():
    if request.method == 'GET':
        return render_template('jquery/login.html')
    email = request.form.get('email')
    passwd = request.form.get('passwd')
    next = request.form.get('next') or url_for('base.base_index')
    user = User.query.filter_by(email=str(email)).first()
    if user is None:
        retdata = {'message':'login failed!', 'result':'failed'}
    else:
        retdata = {'message':'login success!', 'result':'success', 'next':next}
    return json_response(retdata)


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
    except Exception as exp:
        result = 0
        reason = str(exp)
    return json_response({"result":result, "reason":reason})


@rest_api.route('/post', methods=['POST'])
@auth.login_required
def rest_post():
    if request.json is None:
        abort(400)
    body = request.json.get('body', None)
    title = request.json.get('title', None)
    if None in (body, title):
        return json_response({'result':0, 'reason':'params may be wrong'})
    author_id = g.current_user.id
    post = Post()
    Post.on_changed_body(post, body, None, None)
    body_html = post.body_html
    reason = ''
    try:
        sql = "insert into posts(body, body_html, title, timestamp, author_id) \
            values('%s', '%s', '%s', '%s', %d);" %(body, body_html, title, datetime.now(), author_id)
        # db = DataBaseClient()
        with DataBaseClient() as db:
            n = db.execute(sql)
            if n is 0:
                result = 0
            else:
                result = 1
    except Exception as exp:
        result = 0
        reason = str(exp)
    return json_response({'result':result, 'reason':reason})


@rest_api.route('/comment/<int:post_id>', methods=['POST'])
@auth.login_required
def rest_comment(post_id):
    if request.json is None:
        abort(400)
    body = request.json.get('body', None)
    if body is None or post_id == 0:
        return json_response({'result':0, 'reason':'params may be wrong'})
    author_id= g.current_user.id
    comment = Comment()
    Comment.on_changed_body(comment, body, None, None)
    body_html = comment.body_html
    reason = ''
    try:
        select_sql = "select * from posts where post_id=%d;" %post_id
        db = DataBaseClient()
        n = db.execute(select_sql)
        res = db.fetchone()
        if not res:
            result = 0
            reason = 'post not found'
            return json_response({'result':result, 'reason':reason})
        sql = "insert into comments(body, body_html, post_id, author_id, timestamp) \
            values('%s', '%s', %d, %d, '%s');" %(body, body_html, post_id, author_id, datetime.now())
        n = db.execute(sql)
        if n is 0:
            result = 0
        else:
            result = 1
    except Exception as exp:
        result = 0
        reason = str(exp)
    return json_response({'result':result, 'reason':reason})


@rest_api.route('/follower/<int:user_id>', methods=['GET', 'POST'])
@auth.login_required
def rest_follower(user_id):
    if request.method == 'GET':
        sql = "select f.follower_id, u1.email as follower_email, u1.name as follower_name \
        from follows as f left outer join users as u1 on f.follower_id=u1.id \
        where f.followed_id=%d;" % user_id
        with DataBaseClient() as db:
            n = db.execute(sql)
            res = db.fetchall()
        return json_response({'followers':res})
    else:
        reason = ''
        result = 0
        select_sql = 'select * from users where id=%d;' %user_id
        follower_id = g.current_user.id
        sql = "insert into follows(follower_id, followed_id) values(%d, %d)" %(follower_id, user_id)
        with DataBaseClient() as db:
            n = db.execute(select_sql)
            res = db.fetchone()
            if not res:
                reason = 'user not found'
            else:
                n = db.execute(sql)
                result = n
        return json_response({'result':result, 'reason':reason})


@rest_api.route('/followed/<int:user_id>', methods=['GET', 'POST'])
@auth.login_required
def rest_followed(user_id):
    if request.method == 'GET':
        sql = "select f.followed_id, u1.email as followed_email, u1.name as followed_name \
        from follows as f left outer join users as u1 on f.followed_id=u1.id \
        where f.follower_id=%d;" % user_id
        with DataBaseClient() as db:
            n = db.execute(sql)
            res = db.fetchall()
        return json_response({'followeds':res})
    else:
        reason = ''
        result = 0
        select_sql = 'select * from users where id=%d;' %user_id
        followed_id = g.current_user.id
        sql = "insert into follows(follower_id, followed_id) values(%d, %d);" %(user_id, followed_id)
        with DataBaseClient() as db:
            n = db.execute(select_sql)
            res = db.fetchone()
            if not res:
                reason = 'user not found'
            else:
                n = db.execute(sql)
                result = n
        return json_response({'result':result, 'reason':reason})

