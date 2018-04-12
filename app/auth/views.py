from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, login_required

from . import auth
from .forms import RegistrationForm, LoginForm
from ..models import User


@auth.route('/')
def home():
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(uni=form.uni.data,
                 first=form.first.data,
                 last=form.last.data,
                 year=form.grad_year.data,
                 school=form.school.data,
                 password=form.password.data)
        u.save()
        flash('Successfully created account. Please check your email')
        # TODO: send confirmation email
        return redirect(url_for('main.home'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = next(User.find(form.uni.data))
        if u is not None and u.verify_password(form.password.data):
            login_user(u, form.remember.data)
            return redirect(request.args.get('next') or url_for('main.home'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.home'))


@auth.route('/profile')
@login_required
def profile():
    # TODO: show users reviews and votes
    return 'not implemented'
