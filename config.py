import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # TESTING
    SQLALCHEMY_DATABASE_URI= 'sqlite:///' + os.path.join(basedir, 'database.db')
