import os
import datetime

from flask import render_template, redirect, flash, url_for 
from daily import app # unnecessary
from daily.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from daily.models import User


# User index page
@app.route("/")
@login_required
def index():
    """ Show current data on daily """
    return render_template("index.html")


# Route for logging the user in
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): # Check if request was a POST request 
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Log In', form=form)


# Log user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# User grahs and statistics 
@app.route("/graphs")
@login_required
def graphs():
    return render_template("graphs.html")
