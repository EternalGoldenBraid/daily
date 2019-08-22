from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#View module (view functions) must be imported after the application object is created.
from daily import views, models
from flask_login import LoginManager

login = LoginManager(app)
