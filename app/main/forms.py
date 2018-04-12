from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Length(max=128, message='Query too long')])
    submit = SubmitField('submit')

class VoteForm(FlaskForm):
    agree = SubmitField('Agree')
    disagree = SubmitField('Disagree')
