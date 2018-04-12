from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ReviewForm(FlaskForm):
    general = TextAreaField('General Review',
                            validators=[
                                Length(1, 5000),
                                DataRequired('Please comment on the class and/or teacher ability')])
    workload = TextAreaField('Workload Review', validators=[Length(1, 5000)])
    submit = SubmitField('Submit')