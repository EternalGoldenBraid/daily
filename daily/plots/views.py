import os
import requests
import json
from datetime import datetime
from sqlalchemy.exc import (SQLAlchemyError, IntegrityError,
                            InvalidRequestError)
from daily.models import (Rating, Tag, Event, Buffer,
                            rating_as, event_as, BufferEdit)
from daily import db
from daily.helpers import hours_minutes
from flask import (render_template, redirect, flash, url_for,
        request, jsonify, session, abort, current_app)
rom werkzeug.urls import url_parse

from daily.plots import bp


@bp.route("/plots", methods=["GET", "POST"])
@login_required
def plots():

    render_template(url_for(plots.plots.html)
    pass
