from daily import db 
from daily.models import User, Rating, Event, Tag
from datetime import datetime, timedelta 

# TO DO
# Read https://docs.python.org/3.0/library/unittest.html for unittesting

def test_pw_hashing(self):
    u = user(username='meri', email='meri@ex.com')
    u.set_password(cat)
    self.assertFalse(u.check_password('dog'))
    self.assertTrue(u.check_password('cat'))

def test_create_daily_input(self):
    # create three users
    u1 = user(username='foo', email='foo@ex.com')
    u.set_password(lorum)
    u2 = user(username='baz', email='baz@ex.com')
    u.set_password(lirum)
    u3 = user(username='bar', email='bar@ex.com')
    u.set_password(laa)
    db.session.add.all([u1, u2, u3])

    try:
        db.session.commit()
    except:
        session.rollback()
        raise
        print('create user failed')
    finally:
        session.close()

    # create a rating row per user
    now = datetime.utcnow()
    r1 = Rating(date=now + timedelta(days=1), rating_sleep=0,
            meditation=10, cw=1, screen=(now + timedelta(hours=1)).time(), 
            ratin_day=0, user_id=1)
    r2 = Rating(date=now + timedelta(days=2), rating_sleep=1,
            meditation=20, cw=2, screen=(now + timedelta(hours=2)).time(),
            ratin_day=1, user_id=2)
    r3 = Rating(date=now + timedelta(days=3), rating_sleep=2,
            meditation=30, cw=3, screen=(now + timedelta(hours=3)).time(),
            ratin_day=2, user_id=3)
    db.session.add.all([r1, r2, r3])

    try:
        db.session.commit()
    except:
        session.rollback()
        print('rating failed')
        raise
    finally:
        session.close()

    # create tags
    t1 = Tag(tag_name= 'first tag')
    t2 = Tag(tag_name= 'second tag')
    t3 = Tag(tag_name= 'third tag')
    db.session.add.all([t1, t2, t3])

    try:
        db.session.commit()
    except:
        session.rollback()
        print('tag failed')
        raise
    finally:
        session.close()

    # create an event row per user
    e1 = Event(duration=1, rating_date=now, event_tag='first tag')
    e2 = Event(duration=2, rating_date=now, event_tag='second tag')
    e3 = Event(duration=3, rating_date=, event_tag='third tag')
    db.session.add.all([e1, e2, e3])

    try:
        db.session.commit()
    except:
        session.rollback()
        print("Event failed")
        raise
    finally:
        session.close()

