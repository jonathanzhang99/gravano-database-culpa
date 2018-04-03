from flask import render_template, request

from . import main
from .forms import SearchForm
from ..models import Course


@main.route('/')
def home():
    form = SearchForm()
    return render_template('main/home.html', form=form)

@main.route('/search')
def search():
    query = '%'.join(request.args.get('query').split(' '))
    query = f'%{query}%'
    return render_template('main/search.html', courses=Course.search(query))


@main.route('/departments')
def departments():
    return 'not implemented'


@main.route('/departments/<name>')
def department_info(name):
    return str(name)