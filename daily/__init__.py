from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager, UserMixin


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

#View module (view functions) must be imported after the application object is created.
login = LoginManager(app)
login.login_view = 'auth.login'
from daily import models, views 

# Register blueprints
from daily.errors import bp as errors_bp
from daily.auth import bp as auth_bp
app.register_blueprint(errors_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
