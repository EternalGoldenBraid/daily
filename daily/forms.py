from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, 
    SubmitField, DateField, IntegerField)
from wtforms.validators import DataRequired, length


class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')

class EntryForm(FlaskForm):
    date=DateField('Date', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Date"})
    sleep_rating=IntegerField('Sleep', validators=[DataRequired()], render_kw={"placeholder": "Sleep"}) 
    meditation=IntegerField('Meditation', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Meditation"})
    description=StringField('Description', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Description"})
    day_rating=IntegerField('Rating', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Rating"})
    lights=IntegerField('Lights', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Lights"})
    cw=IntegerField('CW', validators=[DataRequired(), length(max=12)], render_kw={"placeholder": "Creative Work"})
    submit=SubmitField('Submit')
