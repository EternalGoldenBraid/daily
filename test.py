# To be used for unit test see 
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
# Under Unit Testing Improvements
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://dev:test@localhost/dailydb'
    SECRET_KEY = 'asd'
    EXPLAIN_TEMPLATE_LOADING = True;

