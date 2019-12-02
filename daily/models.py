from daily import db, login, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
    date = db.Column(db.DateTime, unique=True, nullable=False) # SHOULD DATE BE UNIQUE?  Ok for single user
    rating_sleep = db.Column(db.Integer, index=True, nullable=False)
    meditation = db.Column(db.Integer, nullable=False) # Duration of daily meditation.
    cw = db.Column(db.Numeric(4,2), nullable=False) # Duration of daily creative work. IMPRO: Change to floating point values
    screen = db.Column(db.Time, nullable=False) # When did user stop/reduce bright light exposure.
    rating_day = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)

    # Establish Event objects on Rating called Rating.events.
    # Establish .rating attribute on Event, which refer to the parent Rating object.
    events = db.relationship('Event', backref='rating', lazy='dynamic')

    def __repr__(self):
        return '<User: {} Date: {}, Rating_date : {}, M : {}, CW: {}, Screens: {}>'.format(
    self.user.username, self.date, self.rating_day, self.meditation,
            self.cw, self.screen)
    
# Define events table, by design will have multiple date entries due to multiple unique tags.
# Can probably be improved
# Potential Improvements:
#   When new rating, check if a corresponding event already exists. If yes, use that, else create event.
#       How to code duration, rounding by minute?

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Numeric(4,2)) # Duration of the event, In future integrate with Toggl API, measured in minutes
    rating_date = db.Column(db.DateTime, db.ForeignKey('rating.date'), index=True, nullable=False) # Date of the event
    event_tag = db.Column(db.String, db.ForeignKey('tag.tag_name'), index=True, nullable=False) # Description/tag of the event
    # Add start/stop time pauses?

    
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

# user_loader is a callback(call after) function for reloading the user from session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
