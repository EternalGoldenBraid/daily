from flask import render_template, redirect, url_for, flash
from daily import db
from daily.errors import bp

@bp.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('index')), 404


@bp.errorhandler(500)
def internal_error(error):
    flash(error)
    print(error)
    db.session.rollback()
    return redirect(url_for('index')), 500


@bp.errorhandler(404)
def bad_request_error(error):
    return redirect(url_for('index')), 400


