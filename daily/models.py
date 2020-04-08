from daily import db, login, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3connection


# Define users table
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120) ,index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Establish Rating objects on User called User.ratings.
    # Establish a .user attribute on Rating which referes to the parent User object
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    def __repr__(self):
        return '{},{}'.format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Define daily table
class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    # DATE SHOULD DATE BE UNIQUE?  Ok for single user
    date = db.Column(db.DateTime, unique=True, nullable=False) 
    rating_sleep = db.Column(db.Integer, index=True, nullable=False)
    meditation = db.Column(db.Integer, nullable=False) 
    cw = db.Column(db.Integer, nullable=False) 
    screen = db.Column(db.Integer, nullable=False) 
    rating_day = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                index=True, nullable=False)

    # Establish Event objects on Rating called Rating.events.
    # Establish .rating attribute on Event, 
    # which refer to the parent Rating object.
    events = db.relationship('Event', backref='rating', lazy='dynamic')

    
    
# Define events table, by design will have 
# multiple date entries due to multiple unique tags.
# Potential Improvements:
class Event(db.Model):
    __tablename__ = 'Event'

    id = db.Column(db.Integer, primary_key=True)
    # Duration of the event, In future integrate with Toggl API, measured in minutes
    duration = db.Column(db.Integer) 
    # Date of the event
    rating_date = db.Column(db.DateTime, 
            db.ForeignKey('rating.date'), index=True, nullable=False) 
    # Description/tag of the event
    event_tag = db.Column(db.String, db.ForeignKey('tag.tag_name'), 
            index=True, nullable=False)     
    
    def __repr__(self):
        return '<Date of event is : {}, The even tag is: {}, which had the duration of {}>'.format(self.rating_date, self.event_tag, self.duration)

# Define relationships with tags and days
class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String, index=True, unique=True, nullable=False)

    # Establish Tag object on Event called Event.tags.
    # Establish .event attribute on Tag, which refers to the parent Event object.
    tags = db.relationship('Event', backref='tag', lazy='dynamic')


    def __repr__(self):
        return '<Tag name is {}>'.format(self.tag_name)


# A buffer to hold event: duration pairs for a user during an entry
class Buffer(db.Model):
    __tablename__= 'buffer'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True, nullable=False)
    event_tag = db.Column(db.String, 
            index=True, nullable=False)     
    duration = db.Column(db.Integer) 


    #def __repr__(self):
        #return {self.event_tag: self.duration}



# user_loader is a callback(call after) function for reloading the user from session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# SQLite3 foreign key constraints to be enforced on engine connect
@event.listens_for(Engine, "connect")
def set_sqlite_foreign_key(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3connection):
       cursor=dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON;")
       cursor.close()
