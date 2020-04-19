from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, FormField,
    FieldList, SubmitField, IntegerField)
from wtforms.validators import DataRequired, length, NumberRange
from wtforms.fields.html5 import DateField
from wtforms.widgets import ListWidget


class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')

class DescriptionForm(FlaskForm):
    event=StringField('Event', 
                validators=[length(max=200, 
                message='Keep event under 200 characters')])
    duration_event=IntegerField('Duration', 
            validators=[NumberRange(min=0, max=24, 
                message='Event duration exceeds 24 hours')])
    submit=SubmitField('Submit Events')

class EventsForm(FlaskForm):
    description=FieldList(FormField(DescriptionForm), 
                min_entries=1)
    submit=SubmitField('Submit Events')



## Form for inputting daily evens
#class EntryForm(FlaskForm):
#    date=DateField('Date', format='%Y-%m-%d', 
#                validators=[DataRequired()], 
#                render_kw={"placeholder": "Date"})
#    sleep_rating=StringField('Sleep', validators=[DataRequired()],
#                render_kw={"placeholder": "Sleep"}) 
#    meditation=StringField('Meditation', validators=[DataRequired(),
#                length(max=3, message="Meditation input too long")],
#                render_kw={"placeholder": "Meditation"})
#    #description=StringField('Description', validators=[DataRequired()],
#                #render_kw={"placeholder": "Description"})
#    day_rating=StringField('Rating', validators=[DataRequired(), 
#                length(max=2, 
#                message='Rating for the day contains too many digits')],
#                render_kw={"placeholder": "Rating"})
#    lights=StringField('Lights', validators=[DataRequired(), 
#                length(max=5,
#                message='Your lights input contains too many digits')],
#                render_kw={"placeholder": "Lights"})
#    cw=StringField('CW', validators=[DataRequired(),
#                length(max=5, message= 'CW contains too many digits')],
#                render_kw={"placeholder": "Creative Work"})
#    submit=SubmitField('Submit For the day')

# FOR TESTING
class EntryForm(FlaskForm):
    date=DateField('Date', format='%Y-%m-%d', 
                validators=[DataRequired()], 
                render_kw={"placeholder": "Date"})

    sleep_rating=StringField('Sleep', validators=[DataRequired()],
                render_kw={"placeholder": "Sleep"}, default = 1) 

    meditation=StringField('Meditation', validators=[DataRequired(),
                length(max=15, 
                    message="Meditation contains too many digits")],
                render_kw={"placeholder": "Meditation"}, default = 2)

    day_rating=StringField('Rating', validators=[DataRequired(), 
        length(max=2, message='Rating for the day contains too many digits')
        ],
                render_kw={"placeholder": "Rating"}, default = 3)
    lights=StringField('Lights', validators=[DataRequired(), 
                length(max=15,
                message='Your lights input contains too many digits')],
                render_kw={"placeholder": "Lights"}, default = 4)
    cw=StringField('CW', validators=[DataRequired(),
                length(max=15, message= 'CW contains too many digits')],
                render_kw={"placeholder": "Creative Work"}, default = "11-07-22")
    submit=SubmitField('Submit For the day')



#def validate_date(form, field):
#        if field.data < form.startdate_field.data:
#            raise ValidationError("End date must not be earlier than start date.")

