from flask import render_template, request

from . import main
from .forms import SearchForm
from ..models import Course, Department, Teacher


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
    return render_template('main/departments.html', departments=Department.find_all())


@main.route('/departments/<did>')
def department(did):
    return render_template('main/department.html', department=next(Department.find(did)))


@main.route('/courses/<cid>')
def courses(cid):
    return render_template('main/courses.html', course=next(Course.find(cid)))


@main.route('/teachers/<uni>')
def teacher(uni):
    return render_template('main/teacher.html', teacher=next(Teacher.find(uni)))
