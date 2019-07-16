from flask import Flask 
app = Flask(__name__)


# View module (view functions) must be imported after the application object is created.
import daily.views
# SQLAlchemy for declarative way
from daily.database import db_session

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

