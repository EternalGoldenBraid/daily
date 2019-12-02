from daily import app, db
from daily.models import User, Rating, Event, Tag

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Rating': Rating, 'Event': Event,
            'Tag': Tag}
