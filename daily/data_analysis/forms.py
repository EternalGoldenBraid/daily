from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, FormField,
    FieldList, SubmitField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, length, NumberRange
from wtforms.fields.html5 import DateField
from wtforms.widgets import ListWidget


class KPrototypes_network_form(FlaskForm):
    k=IntegerField('k', 
            render_kw={'placeholder': 'k'},
            validators=[NumberRange(min=0, max=24, 
                message='Clusters exceeding timespan is undefined'),
                DataRequired(),
                ],
            default = 5)
    timespan=IntegerField( 
            render_kw={'placeholder': 'dT'},
            validators=[NumberRange(min=0, max=999, message='Must be positive'),
                DataRequired(),
                ],
            default=14)
    submit=SubmitField('OK')

class KPrototypes_cost_form(FlaskForm):
    k=IntegerField('k', 
            render_kw={'placeholder': 'k'},
            validators=[NumberRange(min=0, max=24, 
                message='Clusters exceeding timespan is undefined'),
                DataRequired(),
                ],
            default=5)
    timespan=IntegerField( 
            render_kw={'placeholder': 'dT'},
            validators=[NumberRange(min=0, max=999, 
                message='Must be positive'),
                DataRequired(),
                ],
            default=14)
    submit=SubmitField('OK')
