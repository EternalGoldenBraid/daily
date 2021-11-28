from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager, UserMixin

## DEBUG
from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
## end DEBUG



db = SQLAlchemy()
#migrate = Migrate(app, db, compare_type=True)
migrate = Migrate(compare_type=True)

#View module (view functions) must be imported after the application object is created.
login = LoginManager()
login.login_view = 'auth.login'
from daily import models 


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    if not app.debug and not app.testing:
        pass

    # Register blueprints
    from daily.main import bp as main_bp
    from daily.auth import bp as auth_bp
    from daily.errors import bp as errors_bp
    from daily.data_analysis import bp as data_bp 
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(errors_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(main_bp)

    return app
