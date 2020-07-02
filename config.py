import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination
    DAYS_PER_PAGE = 7
    EVENTS_PER_PAGE = 4

    if os.environ.get('FLASK_ENV') == 'development':
        SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://daily:test@localhost/database'
        SECRET_KEY = 'asd'
