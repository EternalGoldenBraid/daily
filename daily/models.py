from daily import db


# Define users table
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120) ,index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Establish Rating objects on User called User.ratings.
    # Establish a .user attribute on Rating which referes to the parent User object
    ratings = db.relationship('Rating', backref='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)

# Define daily table
class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    rating_sleep = db.Column(db.Integer, index=True, nullable=False)
    meditation = db.Column(db.Integer, nullable=False) # Duration of daily meditation.
    cw = db.Column(db.Integer, nullable=False) # Duration of daily creative work.
    screen = db.Column(db.Time, nullable=False) # When did user stop bright light exposure.
    rating_day = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)

    # Establish Event objects on Rating called Rating.events.
    # Establish .rating attribute on Event, which refer to the parent Rating object.
    events = db.relationship('Event', backref='rating')

    def __repr__(self):
        return '<Rating of the day: {}, User_id: {}>'.format(self.rating_day, self.user_id)
    
# Define events table

# Read here http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer) # In future integrate with Toggl API 
    rating_date = db.Column(db.Date, db.ForeignKey('rating.date'), index=True, nullable=False)

    tags = db.relationship('Tag', backref='event')

    def __repr__(self):
        return '<Tags {}>'.format(self.username)

# Define relationships with tags and days
class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)

    



