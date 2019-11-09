from daily import db 
from daily.models import User, Rating, Event, Tag
from datetime import datetime, timedelta 


def test_pw_hashing(self):
    u = user(username='meri', email='meri@ex.com')
    u.set_password(cat)
    self.assertFalse(u.check_password('dog'))
    self.assertTrue(u.check_password('cat'))

def test_create_daily_input(self)
    # create three users
    u1 = user(username='foo', email='foo@ex.com')
    u.set_password(lorum)
    u2 = user(username='baz', email='baz@ex.com')
    u.set_password(lirum)
    u3 = user(username='bar', email='bar@ex.com')
    u.set_password(laa)
    db.session.add.all([u1, u2, u3])
    
    if not db.session.commit:
        print('Creating users failed')

    # create a rating row per user
    now = datetime.utcnow()
    r1 = Rating(date=now + timedelta(days=1) , rating_sleep=1, meditation=10 , cw=10 , screen= , ratin_day= , user_id= )
    r2 = Rating(date= , rating_sleep= , meditation= , cw= , screen= , ratin_day= , user_id= )
    r3 = Rating(date= , rating_sleep= , meditation= , cw= , screen= , ratin_day= , user_id= )
    db.session.add.all([r1, r2, r3])

    if not db.session.commit:
        print('Creating ratings failed')

    # create an event row per user
    e1 = Event(duration= , rating_date= , event_tag= )
    e2 = Event(duration= , rating_date= , event_tag= )
    e3 = Event(duration= , rating_date= , event_tag= )
    db.session.add.all([e1, e2, e3])

    if not db.session.commit:
        print('Creating events failed')

    # create tags
    t1 = Tag(tag_name= 'first tag')
    t2 = Tag(tag_name= 'second tag')
    t3 = Tag(tag_name= 'third tag')
    db.session.add.all([t1, t2, t3])

    if not db.session.commit:
        print('Creating tags failed')

