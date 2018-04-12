from flask import render_template
from flask_login import login_required

from . import user
from .forms import ReviewForm


@user.route('/review', methods=['GET', 'POST'])
@login_required
def write_review():
    form = ReviewForm()
    if form.validate_on_submit():
        pass;
    return render_template('user/review.html', form=form)