import os
from datetime import datetime

from sqlalchemy.exc import (SQLAlchemyError, IntegrityError,
                            InvalidRequestError)
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

    # Fetch existing rows from rating table for rendering to user
    ratings = Rating.query.filter_by(user_id=current_user.id)
    rating_event= db.session.query(Rating, Event).filter(
                Rating.date==Event.rating_date).all()
    form_day = EntryForm()
    form_events = DescriptionForm()
    buffers = Buffer.query.filter_by(user_id=current_user.id).all()
    events_buffer = {}

    # Stage current events awaiting confirmation
    for buffer in buffers:
        events_buffer[buffer.event_tag] = buffer.duration

    # Receive and add to database users new row for rating table
    if request.method == 'POST' and form_day.validate():
        rating = Rating(user_id=current_user.id, date=form_day.date.data, 
                rating_sleep=form_day.sleep_rating.data,
                meditation=form_day.meditation.data, cw=form_day.cw.data, 
                screen=form_day.lights.data, 
                rating_day=form_day.day_rating.data)

        # Read tags from user input
        tags = Tag.query.all()
        tags_strings = [tag_str.tag_name for tag_str in tags]
        print(tags_strings)
        # Make sure buffer is non-empty
        if len(events_buffer.items()) > 0:
            for item in events_buffer.items():
                description, duration = item[0], item[1]
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
                        if tag not in tags_strings:
                            new_tag = Tag(tag_name=tag)
                            db.session.add(new_tag)

                            # Associate event with the new tag
                            event_new.tags.append(new_tag)
                        else:
                            # Associate event with the existing tag
                            existing_tag = Tag.query.filter_by(
                                            tag_name=tag).first()
                            print("Found an existing tag!: ",existing_tag.tag_name) # TEST
                            # DEBUG
                            print("Events date: ", event_new.rating_date)
                            print("Existings dates:")
                            for day in Rating.query.all():
                                print(day.date)

                            event_new.tags.append(existing_tag)





                # Associate rating with an event
                rating.events.append(event_new)

        print(f"Rating of day: {rating.date}")
        print(f"Events")
        for e in rating.events:
            print(e.story, end=" With tags:")
            for t in e.tags:
                print(f"{t.tag_name}", end="/")
            print()



        try:
            #db.session.add(rating)
            db.session.commit()

        except (SQLAlchemyError, InvalidRequestError) as e1:
            db.session.rollback()
            print(e1)
            flash("New entry overlaps with old one")

    #SQLinjection safe?
    return  render_template("index.html", 
            rating_event=rating_event, rating=ratings, form_day=form_day,
            form_events=form_events, events=events_buffer)
    

@app.route("/events_confirm", methods=["POST"])
@login_required
def events_confirm():


    # Collect user entered Events: duration pairs untill they signal done
    try:
        data = request.form.to_dict()
        user_id = current_user.id
        event, duration = data['event'].rstrip(), data['duration']
        event = event.upper()
        buffers = Buffer.query.filter_by(user_id=user_id).all()
        events = {}

        # Stage current events awaiting confirmation
        for buffer in buffers:
            events[buffer.event_tag] = buffer.duration

        # Validate that entry does not already exist 
        if Buffer.query.filter_by(user_id = user_id, 
                event_tag=event).all():
            return jsonify("Event already exists"), 409
        
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

# url_parse() Parses a URL from a string into a URL tuple. If the URL is lacking a scheme it can be provided as second argument. Otherwise, it is ignored. Optionally fragments can be stripped from the URL by setting allow_fragments to False.
#The inverse of this function is url_unparse().


# Route for loggine the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
