from daily import db


# Define users table
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

# Define daily table
class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    rating_sleep = db.Column(db.Integer, nullable=False)
    meditation = db.Column(db.Integer, nullable=False)
    cw = db.Column(db.Integer, nullable=False)
    screen = db.Column(db.Time, nullable=False)
    rating_day = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Rating of the day: {}, User_id: {}>'.format(self.rating_day, self.user_id)
    
# Define tags table

# Read here http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/

class Tags(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return '<Tags {}>'.format(self.username)

# Define relationships with tags and days
class Tagmap(db.Model):
    __tablename__ = 'tagmap'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.id'))
