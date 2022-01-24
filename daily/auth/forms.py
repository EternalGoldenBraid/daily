from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, FormField,
    FieldList, SubmitField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, length, NumberRange, Email
from wtforms.fields.html5 import DateField, EmailField
from wtforms.widgets import ListWidget


class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    email=EmailField('Email', validators=[Email()])
    password=PasswordField('Password', validators=[DataRequired()])
    password_confirm=PasswordField('Confirm password', validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')
