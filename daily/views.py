import os
import datetime

from flask import render_template, redirect, flash 
from daily import app
from daily.forms import LoginForm

from daily.helpers import login_required

@app.route("/")
def index():
    """ Show current data on daily """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    form.validate_on_submit
    if form.validate_on_submit():
        flash('Login {}, Remember me {}'.format(form.username.data, form.remember_me.data))
        return redirect('/')
    return render_template('login.html', title='Log In', form=form)
