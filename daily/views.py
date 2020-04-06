import os
import datetime

from sqlalchemy.exc import SQLAlchemyError
from daily import app, db # unnecessary
from daily.forms import (LoginForm, EntryForm, 
                        EventsForm, DescriptionForm)
from flask import (render_template, redirect, flash, 
        url_for, request, jsonify, session)
from flask_login import (current_user, login_user, 
                    logout_user, login_required)
from daily.models import User, Rating, Tag, Event, Buffer
from werkzeug.urls import url_parse
from copy import deepcopy

@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
    Index page of the site, includes a table of daily history
    """

    rating = Rating.query.filter_by(user_id=current_user.id)
    rating_event= db.session.query(Rating, Event).filter(
                Rating.date==Event.rating_date).all()
    form_day = EntryForm()
    form_events = DescriptionForm()
    buffers = Buffer.query.filter_by(user_id=current_user.id).all()
    events = {}

    # Stage current events awaiting confirmation
    for buffer in buffers:
        events[buffer.event_tag] = buffer.duration


    # Store into the database
    # TODO

    #flash(form.errors) # DEBUG

    #SQLinjection safe?
    return  render_template("index.html", 
            rating_event=rating_event, rating=rating, form_day=form_day,
            form_events=form_events, events=events)
    
    
@app.route("/events_confirm", methods=["POST"])
@login_required
def events_confirm():


    # Collect user entered Events: duration pairs untill they signal done
    try:
        data = request.form.to_dict()
        user_id = current_user.id
        event, duration = data['event'].rstrip(), data['duration']
        buffers = Buffer.query.filter_by(user_id=user_id).all()
        events = {}

        # Stage current events awaiting confirmation
        for buffer in buffers:
            events[buffer.event_tag] = buffer.duration

        # Validate that entry does not already exist 
        if Buffer.query.filter_by(user_id = user_id, 
                event_tag=event).all():
            return jsonify(events), 500
        
        # Add to database
        buffer_add = Buffer(user_id = user_id, event_tag= event,
                    duration = duration)
        db.session.add(buffer_add)
        db.session.commit()
    
        # Render to user current events awaiting confirmation
        events[event] = duration
        return jsonify(events)

    except SQLAlchemyError as e:
        print(e)
        return jsonify()


@app.route("/empty", methods=["POST", "GET"])
@login_required
def empty():

    if  Buffer.query.filter_by(
            user_id=current_user.id).delete():
        db.session.commit()

    #testi = db.session.query(Buffer).filter(
                    #Buffer.user_id==current_user.id).all()
    #db.session.delete(testi)

    return jsonify("ok"), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Logs user in
    """

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():         
    # Check if request was a POST request 
        # Attempt to fetch users username from the database, 
        # take the first result
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        # Forward to the page the attempted to get at before authentication
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
