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
# from ..libs.saferedirect import redirect_back
from ..libs.jsonlib import json_response
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

@base.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        return render_template('test.html')
    from flask import jsonify
    email = request.form.get('email')
    passwd = request.form.get('passwd')
    user = User.query.filter_by(email=str(email)).first()
    if user is None:
        retdata = {'message':'login failed!'}
    else:
        retdata = {'message':'login success!'}
    return jsonify(retdata)

@base.route('/')
def base_index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5,
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

@base.route('/login', methods=['POST'])
def base_login():
    if request.method == 'POST':
        if request.json is None:
            email = request.form.get('email')
            passwd = request.form.get('passwd')
            next = request.form.get('next') or url_for('.base_index')
        else:
            email = request.json.get('email')
            passwd = request.json.get('passwd')
            next = request.form.get('next') or url_for('.base_index')
        user = User.query.filter_by(email=str(email)).first()
        if user is not None and user.verify_password(passwd):
            login_user(user)
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            retdata = {'result':True, 'message':'login success!', 'next':next}
            # return redirect_back('base.base_index')
        else:
            retdata = {'result':False, 'message':'Invalid username or password!', 'next':next}
            # flash('Invalid username or password.')
            # return render_template('login.html')
        return json_response(retdata)
        

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
        check_user = User.query.filter_by(email=str(email)).first()
        if check_user is not None:
            flash("The email address has already been registered.")
            return render_template('register.html')

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
    next = url_for('base.base_about')
    return render_template('utils.html', content="About Page", next=next)

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