from flask import Flask, redirect, url_for, render_template, current_app, request, flash
from . import base
from ..models import User, Post
from .. import db
from flask_login import login_user, logout_user, \
     login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed
# login lib
from ..decorators import admin_required, permission_required
from ..models import Permission, Role
from ..libs.email import send_email
import json

@base.app_errorhandler(403)
def forbidden_403(error):
    return render_template("utils.html", content='User Forbidden!')

@base.app_errorhandler(401)
def forbidden_401(error):
    return render_template("utils.html", content='User Unauthorized!')

@base.app_errorhandler(404)
def base_404(error):
    return render_template("utils.html", content='Page Not Found!')

@base.app_errorhandler(500)
def base_500(error):
    return render_template("utils.html", content='Internal Server Error!')

@base.route('/')
def base_index():
    posts = Post.query.all()
    for post in posts:
        print post.author.name, post.body, post.title
    print 'posts:', posts
    return render_template('index.html', posts=posts)

@base.route('/login', methods=['POST', 'GET'])
def base_login():
    if request.method == 'POST':
        if request.json is None:
            email = request.form.get('email')
            passwd = request.form.get('passwd')
        else:
            email = request.json.get('email')
            passwd = request.json.get('passwd')
        user = User.query.filter_by(email=str(email)).first()
        if user is not None and user.verify_password(passwd):
            login_user(user)
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            return render_template('utils.html', content=u'login ok!')
        else:
            flash('Invalid username or password.')
            return render_template('login.html')
    else:
        return render_template('login.html')

@base.route('/logout')
@login_required
def base_logout():
    logout_user()
    return render_template('utils.html', content=u'logout!')

@base.route('/register', methods=['POST', 'GET'])
def base_register_user():
    if request.method=="GET":
        return render_template('register.html')
    else:
        print request.form
        email = request.form.get('email')
        password = request.form.get("password")
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        loginuser = User.query.filter_by(email=str(email)).first()
        login_user(loginuser)
        identity_changed.send(current_app._get_current_object(), identity=Identity(loginuser.id))

        # confirm mail
        token = user.generate_confirmation_token(300)
        send_email(user.email, 'Confirm Your Account', 'email/confirm', 
        user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for("base.base_profile"))

@base.route('/about')
def base_about():
    return render_template('utils.html', content="About Page")

@base.route('/profile')
@login_required
def base_profile():
    userinfo = json.dumps({"email":current_user.email, "user_id":current_user.id})
    return render_template('user.html', user=current_user)

@base.route('/nickname/set', methods=['POST', 'GET'])
@login_required
def base_set_nickname():
    if request.method == 'GET':
        return render_template('userupdate.html')
    else:
        nickname = request.form.get('nickname')
        current_user.name = nickname
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for("base.base_profile"))

@base.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('base.base_index'))
    if current_user.confirm(token):
        flash('You have confirmed your account successfully!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('base.base_index'))