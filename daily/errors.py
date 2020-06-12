from flask import render_template, redirect, url_for, flash
from daily import app, db

@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('index')), 404


@app.errorhandler(500)
def internal_error(error):
    flash(error)
    print(error)
    db.session.rollback()
    return redirect(url_for('index')), 500


@app.errorhandler(400)
def bad_request_error(error):
    return redirect(url_for('index')), 400


@app.errorhandler(400)
def bad_request_error(error):
    return redirect(url_for('index')), 400
