from flask import Flask, redirect, url_for, render_template
from . import base

@base.route('/')
def base_index():
	return render_template('index.html')

@base.route('/login/')
def base_login():
	return redirect(url_for('api_v1.0.login'))