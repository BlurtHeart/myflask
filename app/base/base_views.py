from flask import Flask, redirect, url_for, render_template, request
from . import base

@base.route('/')
def base_index():
	return render_template('index.html')

@base.route('/login')
def base_login():
	return redirect(url_for('api_v1.0.login'))

@base.route('/logout')
def base_logout():
    return redirect(url_for('api_v1.0.logout'))

@base.route('/register', methods=['POST', 'GET'])
def base_register_user():
	if request.method=="GET":
		return render_template('register.html')
	else:
		return redirect(url_for("base.base_index"))

@base.route('/about')
def base_about():
    return redirect(url_for('api_v1.0.about'))

@base.route('/profile')
def base_profile():
    return redirect(url_for('api_v1.0.get_profile'))