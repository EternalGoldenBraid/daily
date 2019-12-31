from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, 
    SubmitField, DateField, IntegerField)
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')

class EntryForm(FlaskForm):
    date=DateField('Date', validators=[DataRequired()])
    sleep_rating=IntegerField('Sleep')
    meditation=IntegerField('Meditation')
    description=StringField('Description')
    day_rating=IntegerField('Rating')
    lights=IntegerField('Lights')
    cw=IntegerField('CW')
