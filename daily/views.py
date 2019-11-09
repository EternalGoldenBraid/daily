import os
import datetime

from flask import render_template, redirect, flash, url_for 
from daily import app # unnecessary
from daily.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from daily.models import User

@app.route("/index")
@app.route("/")
#@login_required
def index():
    """ Show current data on daily """
    return render_template("index.html")

# Route for logging the user in
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return rediret(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): # Check if request was a POST request 
        
        # Attempt to fetch users username from the database, take the first result
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page) != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)

# url_parse() Parses a URL from a string into a URL tuple. If the URL is lacking a scheme it can be provided as second argument. Otherwise, it is ignored. Optionally fragments can be stripped from the URL by setting allow_fragments to False.
#The inverse of this function is url_unparse().


# Route for loggine the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
