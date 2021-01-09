from flask import redirect, render_template, request, session
from functools import wraps
import os
import requests
import urllib.parse




def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def hours_minutes(field_name):
    """
    Format from Hours:Minutes to Minutes
    """
    try:
        hours   = request.form[f'{field_name}_hours']
        minutes = request.form[f'{field_name}_minutes']
    except KeyError:
        raise
    
    # Error  checking and validation for duration input as integers
    if hours == '': hours = 0
    if minutes == '': minutes = 0
    try:
        hours = int(hours)
        minutes = int(minutes)
        duration = hours*60 + minutes
        return duration
    except ValueError as e:
        raise
    
