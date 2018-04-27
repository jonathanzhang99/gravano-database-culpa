from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user

from . import main
from .forms import SearchForm, VoteForm
from ..models import Course, Department, Teacher, Review


@main.route('/')
def home():
    form = SearchForm()
    return render_template('main/home.html', form=form)


@main.route('/search')
def search():
    query = '%'.join(request.args.get('query').split(' '))
    query = f'%{query}%'
    return render_template('main/search.html', courses=Course.search(query), teachers=Teacher.search(query))


@main.route('/departments')
def departments():
    return render_template('main/departments.html', departments=Department.find_all())


@main.route('/departments/<did>')
def department(did):
    return render_template('main/department.html', department=next(Department.find(did)))


@main.route('/courses/<cid>', methods=['GET', 'POST'])
def course(cid):
    form = VoteForm()
    course = next(Course.find(cid))
    course.add_view()
    return render_template('main/course.html', course=course, form=form)


@main.route('/teachers/<uni>', methods=['GET', 'POST'])
def teacher(uni):
    form = VoteForm()
    return render_template('main/teacher.html', teacher=next(Teacher.find(uni)), form=form)


@main.route('/review')
def review_redirect():
    return redirect(url_for('user.review'))


@main.route('/vote/<rid>', methods=['POST'])
def vote(rid):
    if current_user.is_anonymous:
        # TODO: make sure that the next variable is set for login to go to the right page
        return jsonify({'message':'redirect', 'url':url_for('auth.login')})
    form = VoteForm()
    message = ''
    if form.validate_on_submit():
        liked = form.agree.data
        v = current_user.get_vote(rid)

        # if user has not previously voted we add a new vote
        if not v:
            current_user.vote(rid, liked)
            message = 'added new vote'

        # if user changed vote, we update the vote
        elif v.liked != liked:
            current_user.update_vote(rid, liked)
            message = 'changed vote'

        else:
            message = 'no effect'

    agree, disagree = next(Review.find(rid)).get_votes()
    return jsonify(
        {
            'message': message,
            'votes' :
                 {
                     'agree': f'Agree {agree}',
                     'disagree': f'Disagree {disagree}'
                 },
            'rid': rid
        }
    )

