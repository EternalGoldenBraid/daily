from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#View module (view functions) must be imported after the application object is created.
login = LoginManager(app)
login.login_view = 'login'
from daily import  models, views
