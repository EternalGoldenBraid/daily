from flask import Flask 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////database.py'
db = SQLAlchemy(app)


# View module (view functions) must be imported after the application object is created.
import daily.views
# SQLAlchemy for declarative way
from daily.database import db_session


