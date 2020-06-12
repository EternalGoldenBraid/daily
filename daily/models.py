from daily import db, login, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, schema
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
    date = db.Column(db.DateTime, unique=False, nullable=False) 
    rating_sleep = db.Column(db.Integer, index=True, nullable=False)
    meditation = db.Column(db.Integer, nullable=False) 
    cw = db.Column(db.Integer, nullable=False) 
    screen = db.Column(db.Integer, nullable=False) 
    rating_day = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                index=True, nullable=False)

    __table_args__ = (
       db.UniqueConstraint('date', 'user_id', name='date_userid'),
    )

# Many-to-many association table for Rating-Event
rating_as = db.Table('rating_events',
        db.Column('rating_id', db.Integer, db.ForeignKey('rating.id')),
        db.Column('event.id', db.Integer, db.ForeignKey('event.id'))
        )

    
# Define events table, by design will have 
# multiple date entries due to multiple unique tags.
# Potential Improvements:
class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer) 
    rating_date = db.Column(db.DateTime, index=True, nullable=False) 
    story = db.Column(db.String(2000), nullable=False, index=True)

    # Many-to-many for rating-events, defines an Rating.events attribute
    rating_events = db.relationship('Rating', secondary=rating_as,
                    backref='events', lazy='dynamic')
                    #cascade="save-update, merge, delete")
    

# Many-to-many association table for Event-Tag
event_as = db.Table('event_tags',
        db.Column('event.id', db.Integer, db.ForeignKey('tag.id')),
        db.Column('tag.id', db.Integer, db.ForeignKey('event.id'))
        )


# Define relationships with tags and days
class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(200), index=True, unique=True,    
                 nullable=False)

    # Many-to-many for events-tags, defines a Event.tags attribute
    tags = db.relationship('Event', secondary=event_as, 
            backref='tags', lazy='dynamic')
            #cascade="save-update, merge, delete",


# A buffer to hold event: duration pairs for a user during an entry
class Buffer(db.Model):
    __tablename__= 'buffer'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True, nullable=False)
    event_tag = db.Column(db.String(2000), unique=True,
            index=True, nullable=False)     
    duration = db.Column(db.Integer) 


# A buffer to hold event: duration pairs for a user during editing rows
class BufferEdit(db.Model):
    __tablename__= 'buffer_edt'

    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, index=True, nullable=False)
    event_tag= db.Column(db.String(2000), unique=True,
            index=True, nullable=False)     
    duration= db.Column(db.Integer) 



# user_loader is a callback(call after) function for reloading 
# the user from session
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
