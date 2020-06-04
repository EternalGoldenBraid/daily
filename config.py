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


 #TESTING
   # SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(basedir, 'database.db')
   # SECRET_KEY = 'adb'
