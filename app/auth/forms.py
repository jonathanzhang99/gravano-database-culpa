from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError, Regexp

from ..models import User


class RegistrationForm(FlaskForm):
    schools = [('cc', 'Columbia College'),
               ('seas', 'School of Engineering and Applied Sciences'),
               ('gs', 'General Studies'),
               ('barnard', 'Barnard'),
               ('grad', 'Graduate School')
               ]
    uni = StringField('uni', validators=[DataRequired('A uni is required!'),
                                         Length(1, 10),
                                         Regexp('^[A-Za-z]+[0-9]+$',
                                                message='Invalid uni')])
    first = StringField('First Name', validators=[DataRequired('A name is required'),
                                                  Length(max=128),
                                                  Regexp('^[A-Za-z\-]*',
                                                         message='Invalid characters in name')])
    last = StringField('Last Name', validators=[DataRequired('A name is required'),
                                                Length(max=128),
                                                Regexp('^[A-Za-z\-]*',
                                                       message='Invalid characters in name')])
    grad_year = IntegerField('Year', validators=[DataRequired('Graduation year required'),
                                                 NumberRange(min=1754,
                                                             max=datetime.now().year + 6,
                                                             message='Please enter a valid year')])
    school = SelectField('School', validators=[DataRequired('Choose your current school of study')],
                         choices=schools)
    password = PasswordField('Password', validators=[DataRequired('Password required'),
                                                     Length(1, 128),
                                                     EqualTo('password2', 'Passwords must match')])
    password2 = PasswordField('Verify Password', validators=[DataRequired('Validate your password')])
    submit = SubmitField('Register')

    def validate_uni(form, field):
        if User.find(field.data) is not None:
            raise ValidationError('User already created – please login')

class LoginForm(FlaskForm):
    uni = StringField('uni', validators=[DataRequired('A uni is required!'),
                                         Length(1, 10),
                                         Regexp('^[A-Za-z]+[0-9]+$',
                                                message='Invalid uni')])
    password = PasswordField('Password', validators=[DataRequired('Password is required')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

