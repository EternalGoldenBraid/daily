import os
from copy import deepcopy
from datetime import datetime
from sqlalchemy.exc import (SQLAlchemyError, IntegrityError,
                            InvalidRequestError)
from daily.models import (User, Rating, Tag, Event, Buffer, 
                            rating_as, event_as, BufferEdit)
from daily import app, db # unnecessary
from daily.forms import (LoginForm, EntryForm, 
                        EventsForm, DescriptionForm)
from daily.helpers import hours_minutes
from daily.errors import bad_request_error, internal_error
from flask import (render_template, redirect, flash, 
        url_for, request, jsonify, session, abort)
from flask_login import (current_user, login_user, 
                    logout_user, login_required)
from werkzeug.urls import url_parse


@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """
    Index page of the site, includes a table of daily history
    """

    # Fetch existing rows from rating table for rendering to user
    page = request.args.get('page', 1, type=int)
    ratings = Rating.query.filter_by(user_id=current_user.id).order_by(
            Rating.date.desc()).paginate(
            page, app.config['DAYS_PER_PAGE'], False)

    next_url = url_for('index', page=ratings.next_num) \
        if ratings.has_next else None
    prev_url = url_for('index', page=ratings.prev_num) \
        if ratings.has_prev else None

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

        try:
            scr = form_day.lights.data.replace(':','')
            scr = int(scr)
        except TypeError:
            print("Error line 71" )
            return bad_request_error(
                "Please enter numbers on screens field")

        rating = Rating(user_id=current_user.id, date=form_day.date.data,
                rating_sleep=form_day.sleep_rating.data,
                meditation=meditation, cw=cw,
                screen=scr,
                rating_day=form_day.day_rating.data)

        # Push a new rating row to database
        try:
            db.session.add(rating)
            db.session.commit()
        except (SQLAlchemyError, InvalidRequestError) as e1:
            db.session.rollback()
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


    # Get the updated ratings
    ratings = Rating.query.filter_by(user_id=current_user.id).order_by(
            Rating.date.desc()).paginate(
            page, app.config['DAYS_PER_PAGE'], False)

    return render_template("index.html",
           ratings=ratings.items, form_day=form_day,
           form_events=form_events, events=events_buffer,
           next_url=next_url, prev_url=prev_url)


@app.route("/events_confirm", methods=["POST"])
@login_required
def events_confirm():

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
        return redirect(url_for('index')), 200
        # For when we decide use an asych rendering of the confirmevents
        # table.
        #return jsonify(events)

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
    print(request.values.get('value'))
    print(request.values.get('id'))
    if event == 'delete':
        # Remove event from buffer
        try:
            id = request.form.get('id')
            buffer = Buffer.query.filter_by(id=id).first()
            db.session.delete(buffer)
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            flash("Something went wrong removing your entry")
            return '', 500
    elif event == 'edit':
       return 'edit not implemented', 404
    return f'{event} OK', 200

@app.route("/delete_edit_row/<id>", methods=["POST", "GET"])
@login_required
def delete_edit_row(id):
    """
    Delete or edit entries from Rating table.
    In case of edit, events are copied into a edit buffer table which's
    contents, after edit, are compared to the corresponding events in
    events table. Changes are made into events table if necessary.
     """

    form_day = EntryForm()
    form_events = DescriptionForm()

    # TEST
    for i in request.form.values():
       print(i)
    print("Rating id: ", id)
    if 'cancel' in request.form.values():
        print("OK")
        clear_bf_edit = BufferEdit.query.filter_by(
                user_id=current_user.id).first()
        db.session.delete(clear_bf_edit)
        db.session.commit()
        return redirect(url_for('index'))

    rating = Rating.query.filter_by(id=id).first()
    events = rating.events

    # Check if request is to delete
    if 'DELETE_rating' in request.form.values():
        # Remove rating event association
        print("Enter delition branch")
        try:
            print("Attempting to delete event from rating") # BBG
            for event in events:
                db.session.delete(event)
            print("delete sucess") # DBG
            print("Attempting to commit") # DBG
            db.session.commit()
            print("commit sucess") # DBG
            print("Attempting to delete rating") # DBG
            db.session.delete(rating)
            print("delete sucess") # DBG
            print("Attempting to commit deletion") # DBG
            db.session.commit()
            print("commit sucess") # DBG
        except SQLAlchemyError as e:
            print(e)
            request.status = 400
            flash("Something went wrong removing your entry")
            return redirect(url_for('index')), 400
    elif 'EDIT_rating' in request.form.values():
        # Render edit page for making changes
        try:
            form_day = EntryForm()
            form_events = DescriptionForm()
            # Copy current events into buffer_edit table
            # for processing edits
            for event in events:
                buffer_edit = BufferEdit(user_id=current_user.id,
                        event_tag=event, duration=event.duration)
                db.session.add(buffer_edit)
                db.session.commit()

            # Format the screens 4 digit int format into HH:MM
            screen_hours = str(rating.screen // 100)
            screen_minutes = str(rating.screen % 100)
            if len(screen_hours) != 2:
                screen_hours = '0'+screen_hours
            if len(screen_minutes) != 2:
                screen_minutes = '0'+screen_minutes
            screen_time=screen_hours+':'+screen_minutes

            return render_template("edit_rating.html", 
                rating=rating, form_day=form_day,
                form_events=form_events, events=events,
                screen_hours=screen_hours, 
                screen_minutes=screen_minutes,
                screen_time=screen_time)

        except SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            clear_bf_edit = BufferEdit.query.filter_by(
                    user_id=current_user.id).first()
            db.session.delete(clear_bf_edit)
            db.session.commit()
            flash("Failed to process your edit request")

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


# Route for loggine the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
