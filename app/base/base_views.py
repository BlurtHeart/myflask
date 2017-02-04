from flask import Flask, redirect, url_for, render_template
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

@base.route('/about')
def base_about():
    return redirect(url_for('api_v1.0.about'))

@base.route('/profile')
def base_profile():
    return redirect(url_for('api_v1.0.get_profile'))