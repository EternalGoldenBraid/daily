import os
import datetime

from flask import Flask, render_template, request


from helpers import login_required

app = Flask(__name__)

@app.route("/")
def index():
    """ Show current data on daily """

    return render_template("index.html")


@app.route("/login")
@login_required
def login():
    error = None

    # Request method was POST
    if request.method == 'POST':

        # Query db for existing credentials
        if db.execute("SELECT ..."):

           # Log user in
           log_in
           return redirect("/")
        else:
           error = 'Invalid username/password'

    # Request method was GET
    return render_template('login.html', error = error)
