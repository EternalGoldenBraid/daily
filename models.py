from sqlalchemy import Column, Integer, String
from daily.database import Base

class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    pw_hash = Column(String(120))
    email = Column(String(120), unique=True)

    def __init__(self, name=None, pw_hash=None, email=None):
        self.name = name
        self.pw_hash = pw_hash
        self.email = email

    def __repr__(self):
        return '<User {}'.format(self.name)
