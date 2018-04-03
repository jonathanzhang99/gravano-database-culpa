from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.find(user_id)


class User(UserMixin):
    def __init__(self, uni, first, last, year, password_hash=None, password=None, school=None, num_reviews=0):

        # needed for flask login
        self.id = uni

        self.uni = uni
        self.first = first
        self.last = last
        self.name = ', '.join([self.last, self.first])
        self.year = year
        if password_hash:
            self.password_hash = password_hash
        else:
            self.password = password
        self.school = school
        self.num_reviews = num_reviews

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.engine.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)',
                          (self.uni,
                           self.name,
                           self.year,
                           self.password_hash,
                           self.school,
                           self.num_reviews)
                          )

    def get_reviews(self):
        return Review.find(self.uni, 'uni')

    @staticmethod
    def find(val, field='uni'):

        query = 'SELECT * FROM users WHERE {} = %s'.format(field)
        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        for (uni, name, year, password_hash, school, num_reviews) in cur:
            yield User(uni=uni,
                       first=name.split(', ')[1],
                       last=name.split(', ')[0],
                       year=year,
                       password_hash=password_hash,
                       school=school,
                       num_reviews=num_reviews)
        cur.close()


class Review(object):
    def __init__(self, c_id, uni, t_uni, general, workload, sentiment_score=0, written_on=None, r_id=None):
        self.c_id = c_id
        self.uni = uni
        self.t_uni = t_uni
        self.general = general
        self.workload = workload
        self.sentiment_score = sentiment_score
        if written_on:
            self.written_on = written_on
        else:
            self.written_on = datetime.now()
        self.r_id = r_id

    def save(self):
        db.engine.execute('''
            INSERT INTO reviews (c_id, uni, teacher_uni, general_content, workload_content, sentiment_score, written_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (self.c_id, self.uni, self.t_uni, self.general, self.workload, self.sentiment_score, self.written_on))

    @staticmethod
    def find(val, field='r_id'):
        query = 'SELECT * FROM reviews WHERE {} = %s'.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        for (r_id, c_id, uni, t_uni, g_content, w_content, s_score, written_on) in cur:
            yield Review(c_id,
                         uni,
                         t_uni,
                         g_content,
                         w_content,
                         s_score,
                         written_on,
                         r_id)
        cur.close()


class Department(object):
    def __init__(self, did, name, abbrev):
        self.did = did
        self.name = name
        self.abbrev = abbrev

    def save(self):
        db.engine.execute('INSERT INTO departments VALUES (%s, %s)', (self.did, self.name, self.abbrev))

    @staticmethod
    def find(val, field='d_id'):
        query = 'SELECT * FROM departments WHERE {} = %s'.format(field)
        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        if cur.rowcount == 1:
            return Department(*cur.fetchone)

        for (did, name, abbrev) in cur:
            yield Department(did, name, abbrev)

        cur.close()

    @staticmethod
    def search(query):
        cur = db.engine.execute('SELECT * FROM departments WHERE LOWER(name) LIKE LOWER(%s)', (query,)
                                )
        if cur.rowcount == 0:
            return None

        for (did, name, abbrev) in cur:
            yield Department(did, name, abbrev)

        cur.close()


class Teacher(object):
    def __init__(self, uni, name, departments=None, courses=None):
        """

        :param uni: uni id
        :param name: last, first
        :param departments: list of department ids
        """

        self.uni = uni
        self.name = name
        self.departments = departments
        self.courses = courses

    def save(self):
        # insert teacher
        db.engine.execute('INSERT INTO teachers VALUES (%s, %s)', (self.uni, self.name))

        # insert teacher department relationships
        for did in self.departments:
            db.engine.execute('INSERT INTO teachers_department VALUES (%s, %s)', (self.uni, did))

    def get_courses(self):
        # TODO: Did not account for the fact that teachers can teach the same class in different semesters

        if not self.courses:
            cur = db.engine.execute('SELECT t.c_id FROM teaches t WHERE t.uni = %s', (self.uni,))
            self.courses = [next(Course.find(cid)) for (cid,) in cur]

        return self.courses

    def get_departments(self):
        if not self.departments:
            cur = db.engine.execute('SELECT td.d_id FROM teachers_department td WHERE td.uni = %s', (self.uni,))
            self.departments = [(Department.find(did)) for (did,) in cur]
        return self.departments

    @staticmethod
    def find(val, field='uni'):
        query = 'SELECT * FROM teachers WHERE {} = %s'.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        for (uni, name) in cur:
            yield Teacher(uni, name)


class Course(object):
    def __init__(self, c_id, name, abbrev, departments=None, teachers=None):
        self.c_id = c_id
        self.name = name
        self.abbrev = abbrev
        self.departments = departments
        self.teachers = teachers

    def get_departments(self):
        if not self.departments:
            cur = db.engine.execute('SELECT cd.d_id FROM course_department cd WHERE cd.c_id = %s', (self.c_id, ))
            self.departments = [next(Department.find(did)) for (did,) in cur]
        return self.departments

    def get_teachers(self):
        if not self.teachers:
            cur = db.engine.execute('SELECT ts.uni FROM teaches ts WHERE ts.c_id = %s ', (self.c_id,))
            self.teachers = [next(Teacher.find(uni)) for (uni,) in cur]
        return self.teachers

    @staticmethod
    def find(val, field='r_id'):
        query = 'SELECT * FROM courses WHERE {} = %s'.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        for (c_id, name, abbrev) in cur:
            yield Course(c_id, name, abbrev)

        cur.close()

    @staticmethod
    def search(query):
        cur = db.engine.execute(
            '''SELECT c.c_id, c.name, c.abbrev
               FROM courses c
               WHERE LOWER(c.name) LIKE LOWER(%s)
               ''', (query,))
        if cur.rowcount == 0:
            return None

        for (c_id, name, abbrev) in cur:
            yield Course(c_id, name, abbrev)
