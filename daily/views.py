import os
from copy import deepcopy
from datetime import datetime
from sqlalchemy.exc import (SQLAlchemyError, IntegrityError,
                            InvalidRequestError)
from daily.models import (User, Rating, Tag, Event, Buffer, 
                            rating_as, event_as)
from daily import app, db # unnecessary
from daily.forms import (LoginForm, EntryForm, 
                        EventsForm, DescriptionForm)
from daily.helpers import hours_minutes
from daily.errors import bad_request_error
from flask import (render_template, redirect, flash, 
        url_for, request, jsonify, session, abort)
from flask_login import (current_user, login_user, 
                    logout_user, login_required)
from werkzeug.urls import url_parse


@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
    Index page of the site, includes a table of daily history
    """

    # Fetch existing rows from rating table for rendering to user
    ratings = Rating.query.filter_by(user_id=current_user.id)
    #rating_event= db.session.query(Rating, Event).filter(
                #Rating.date==Event.rating_date).all()
    form_day = EntryForm()
    form_events = DescriptionForm()
    buffers = Buffer.query.filter_by(user_id=current_user.id).all()
    events_buffer = {}

    # Stage current events awaiting confirmation in dictionary form
    # Key being the str field of the event and value it's duration
    for buffer in buffers:
        events_buffer[buffer.event_tag] = [buffer.duration, buffer.id]

    # Add to database users new row for rating table
    if request.method == 'POST' and form_day.validate():

        # Format the requests hours:minutes representation to minutes
        try:
            cw = hours_minutes('cw')
            meditation = hours_minutes('meditation')
        except ValueError as e:
            print(e)
            return bad_request_error(
                    'Make sure your Creative work hours and Meditation' 
                    + 'inputs are integers')

        rating = Rating(user_id=current_user.id, date=form_day.date.data, 
                rating_sleep=form_day.sleep_rating.data,
                meditation=meditation, cw=cw, 
                screen=form_day.lights.data, 
                rating_day=form_day.day_rating.data)

        # Push a new rating row to database
        try:
            db.session.add(rating)
            db.session.commit()
        except (SQLAlchemyError, InvalidRequestError) as e1:
            db.session.rollback()
            return internal_error("New entry overlaps with old one")
            flash("New entry overlaps with old one")
            return redirect(url_for('index')), 409

        # Read tags from user input
        tags = Tag.query.all()
        tags_strings = [tag_str.tag_name for tag_str in tags]

        # Make sure buffer is non-empty
        if len(events_buffer.items()) > 0:
            for item in events_buffer.items():
                description, duration = item[0], item[1][0]
                parts = description.split(':')
                story = parts.pop(-1)

                # Add Event table row including: date, tag(s), story
                event_new = Event(duration=duration,
                       rating_date=form_day.date.data,
                       story=story)

                # Check if tag exists, TODO: A better validation?
                # This assumes always a story!
                # No tag only inputs expected. Bad design?
                if len(parts) > 0:

                    # Add tags to db if they're new
                    for tag in parts:
                        tag = (tag.rstrip()).upper()
                        if tag not in tags_strings:
                            new_tag = Tag(tag_name=tag)
                            db.session.add(new_tag)
                            db.session.commit()

                            # Update the tag_strings
                            tags_strings.append(tag)

                            # Associate event with the new tag
                            event_new.tags.append(new_tag)
                        else:
                            # Associate event with the existing tag
                            existing_tag = Tag.query.filter_by(
                                            tag_name=tag).first()
                            event_new.tags.append(existing_tag)
                            db.session.add(event_new)

                # Associate rating with an event
                try:
                    rating.events.append(event_new)
                    db.session.commit()
                except SQLAlchemyError as e:
                    print(e)
                    return redirect(url_for('index')), 400


    # Fetch existing events for rendering the all ratings table
    #events_all = Rating.query.filter_by(
            #rating.user_id==current_user.id).all()


    #SQLinjection safe?
    return  render_template("index.html", 
            ratings=ratings, form_day=form_day,
            form_events=form_events, events=events_buffer)
    

@app.route("/events_confirm", methods=["POST"])
@login_required
def events_confirm():

    # Collect user entered Events: duration pairs untill they signal done
    try:
        user_id = current_user.id

        # Collect and validate the event entry from event field
        event = request.form.get('event').rstrip()
        if event == '':
            return 'Please add a note to the event field', 400

        # Format the requests hours:minutes representation to minutes
        try:
            duration = hours_minutes('duration')
        except ValueError as e:
            print(e)
            return jsonify(
                    'Make sure your duration inputs are integers'), 400

        buffers = Buffer.query.filter_by(user_id=user_id).all()
        events = {}

        # Stage current events awaiting confirmation
        for buffer in buffers:
            events[buffer.event_tag] = buffer.duration

        # Validate that entry does not already exist 
        if Buffer.query.filter_by(user_id = user_id, 
                event_tag=event).all():
            return jsonify("Event already exists"), 400
        
        # Add to database
        buffer_add = Buffer(user_id = user_id, event_tag= event,
                    duration = duration)
        db.session.add(buffer_add)
        db.session.commit()
    
        # Render to user current events awaiting confirmation
        # Pass empty string is no duration to render an empty row with
        #   tableconfirmation.js
        if duration != 0:
            events[event] = duration
        else:
            events[event] = ''
        return jsonify(events)

    except SQLAlchemyError as e:
        print(e)
        print("Unexpected error in events_confirm")
        return jsonify()


@app.route("/empty", methods=["POST", "GET"])
@login_required
def empty():

    if Buffer.query.filter_by(
            user_id=current_user.id).delete():
        db.session.commit()
    return "Table emptied", 200


@app.route("/delete_row_buffer", methods=["POST", "GET"])
@login_required
def delete_row_buffer():
    """
    Delete entries from Buffer table:
     Buffer deletions done asynchronously with json
     """

    # Check if request is to delete
    event = request.form.get('value')
    if event == 'BUFFER_delete':
        # Remove event from buffer
        try:
            return redirect(url_for('index'))
            id = none
            buffer = Buffer.query.filter_by(id=id).first()
            db.session.delete(buffer)
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            request.status = 400
            flash("Something went wrong removing your entry")
            return redirect(url_for('index')), 400
    elif event == 'BUFFER_edit':
        pass
    return redirect(url_for('index'))


@app.route("/delete_row/<id>", methods=["POST", "GET"])
@login_required
def delete_row(id):
    """
    Delete entries from Rating table and Buffer table:
     Rating deletions happen synchronously,
     Buffer deletions done asynchronously with json
     """


    # Check if request is to delete
    if 'DELETE_rating' in request.form.values():
        # Remove rating event association
        try:
            rating = Rating.query.filter_by(id=id).first()
            events = rating.events

            for event in events:
                db.session.delete(event)

            db.session.commit()
            db.session.delete(rating)
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            request.status = 400
            flash("Something went wrong removing your entry")
            return redirect(url_for('index')), 400
    elif 'EDIT_rating' in request.form.values():
        pass
    return redirect(url_for('index'))

@app.route("/editRow", methods=["POST", "GET"])
def edit_row():
    return redirect(url_for('index')) 

@login_required
def edit_row():

    if True:
        pass
    return "Table emptied", 200


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

# url_parse() Parses a URL from a string into a URL tuple. 
#If the URL is lacking a scheme it can be provided as second argument. 
#Otherwise, it is ignored. Optionally fragments can be stripped from 
#the URL by setting allow_fragments to False.
#The inverse of this function is url_unparse().

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers user 
    """

    # Awaiting rating table modification for multi user support
    return url_for('register')

#    if form.password != form.password_confimation:
#        flash("Passwords don't match")
#        return redirect(url_for('register'))
#
#    if current_user.is_authenticated:
#        return redirect(url_for('index'))
#    form = RegisterForm()
#    if form.validate_on_submit():         
#    # Check if request was a POST request 
#
#        # Check if user already exists
#        username = form.username.data
#        user = User.query.filter_by(username=username).first()
#
#        if user is not None:
#            flash('Username already exists')
#            return redirect(url_for('register'))
#
#        # Create user
#        u = User(username=username, email=#TODO)
#        u.set_password(form.password.data)
#
#        login_user(user, remember=form.remember_me.data)
#        next_page = request.args.get('next')
#        
#        # Forward to the page the attempted to get at before authentication
#        if not next_page or url_parse(next_page) != '':
#            return redirect(url_for('index'))
#
#        return redirect(next_page)
#
#    return render_template('login.html', title='Log In', form=form)

# url_parse() Parses a URL from a string into a URL tuple. 
#If the URL is lacking a scheme it can be provided as second argument. 
#Otherwise, it is ignored. Optionally fragments can be stripped from 
#the URL by setting allow_fragments to False.
#The inverse of this function is url_unparse().


# Route for loggine the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
