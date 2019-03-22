#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response, render_template, current_app, \
     session, url_for, redirect, flash, abort
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask_login import login_user, logout_user, \
     login_required, current_user
from datetime import timedelta
from flask_cors import CORS
from . import api
from .. import db
from .forms import PostForm, CommentForm

# login lib
from ..decorators import admin_required, permission_required
from ..models import Permission, Role, User, Post, Comment

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
    form = PostForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        body = request.form.get('body')
        title = request.form.get('title')
        author = current_user._get_current_object()
        post = Post(body=body, author=author, title=title)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('base.base_index'))
    else:
        form.body.render_kw = {'style':'height:275px;'}
        return render_template('edit_post.html', form=form)


@api.route('/post/update/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def update_articles(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
                not current_user.can(Permission.ADMINSTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The article has been update.')
        return redirect(url_for('.get_post_by_id', id=post.id))
    form.body.data = post.body
    form.body.render_kw = {'style':'height:275px;'}
    form.title.data = post.title
    form.title.render_kw = {'readonly':'True'}
    # or
    # form.title.render_kw = {'disabled':'True '}
    # form.title.render_kw = {'onfocus':'this.blur()'}
    return render_template('edit_post.html', form=form)


@api.route('/post/show/<id>', methods=['GET', 'POST'])
@login_required
def get_post_by_id(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                        post=post,
                        author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published')
        return redirect(url_for('.get_post_by_id', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / 5 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
                page, per_page=5, error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, 
                        comments=comments, pagination=pagination)


@api.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
                page, per_page=5, error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                        pagination=pagination, page=page)


@api.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@api.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


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
    if request.method == 'GET':
        return get_test()
    elif request.method == 'POST':
        return post_test()
    else:
        return 'Unknown Method'

if __name__ == '__main__':
    api.run(debug=True, host='127.0.0.1', port=8000)
