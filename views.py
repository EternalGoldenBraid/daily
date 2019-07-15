import os
import datetime

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from daily import app

from daily.helpers import login_required

@app.route("/")
def index():
    """ Show current data on daily """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():


    # Forget any user_id
    session.clear()

    # Request method was POST
    if request.method == 'POST':

        # Ensure valid user input
        if not request.form.get("username"):
            return ("Invalid username")

        # Query db for existing credentials

           # Log user in
        else:
            return redirect("/")

    # Request method was GET
    else:
        return render_template("login.html")
