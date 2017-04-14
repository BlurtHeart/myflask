#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response, render_template, current_app, \
     session, url_for, redirect, flash
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask_login import login_user, logout_user, \
     login_required, current_user
from datetime import timedelta
from flask_cors import CORS
from . import api
from .. import db

# login lib
from ..decorators import admin_required, permission_required
from ..models import Permission, Role, User, Post

@api.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@login_required
@admin_required
@api.route('/admin')
def for_admins_only():
    return 'For Administrators'

@api.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return 'For Comment Moderators'

@api.route('/profile/<int:userid>')
@login_required
def otheruser_profile(userid):
    if current_user.id == userid:
        return redirect(url_for('base.base_profile'))

    user = User.query.filter_by(id=userid).first()
    if not user:
        return render_template('utils.html', content='没有此用户！')
    follows = [{'user':item.follower, 'timestamp':item.timestamp}
                for item in user.followers]
    return render_template('otheruser.html', user=user, follows=follows)

@api.route('/post', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_articles():
    if request.method == 'POST':
        body = request.form.get('body')
        title = request.form.get('title')
        author = current_user._get_current_object()
        post = Post(body=body, author=author, title=title)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('base.base_index'))
    else:
        return render_template('editpost.html')

@api.route('/post/show/<id>')
def get_post_by_id(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post.html', post=post)

@api.route('/follow/<userid>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('base.base_index'))
    if current_user.is_following(user):
        flash('You have already followed this user')
        return redirect(url_for('.otheruser_profile', userid=user.id))
    current_user.follow(user)
    flash('You are now following %s' % user.name)
    return redirect(url_for('.otheruser_profile', userid=user.id))

@api.route('/unfollow/<userid>')
@login_required
def unfollow(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('base.base_index'))
    current_user.unfollow(user)
    return redirect(url_for('.otheruser_profile', userid=user.id))

@login_required
def get_test():
    return 'get test'

@login_required
def post_test():
    return 'post test'

@api.route('/test', methods=['GET', 'POST'])
def test():
    print request.headers
    print request.path
    if request.method == 'GET':
        return get_test()
    elif request.method == 'POST':
        return post_test()
    else:
        return 'Unknown Method'

if __name__ == '__main__':
    api.run(debug=True, host='127.0.0.1', port=8000)
