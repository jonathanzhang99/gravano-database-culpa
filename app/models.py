from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return next(User.find(user_id))


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

    def get_vote(self, rid):
        return Vote.find(self.uni, rid)

    def vote(self, rid, liked):
        v = Vote(self.uni, rid, liked)
        v.save()

    def update_vote(self, rid, liked):
        db.engine.execute('UPDATE votes SET liked = %s WHERE (uni, r_id) = (%s, %s)', (liked, self.uni, rid))

    @staticmethod
    def find(val, field='uni'):

        query = 'SELECT * FROM users WHERE {} = %s'.format(field)
        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        def user_generator():
            for (uni, name, year, password_hash, school, num_reviews) in cur:
                yield User(uni=uni,
                           first=name.split(', ')[1],
                           last=name.split(', ')[0],
                           year=year,
                           password_hash=password_hash,
                           school=school,
                           num_reviews=num_reviews)
            cur.close()

        return user_generator()

class Vote(object):
    def __init__(self, uni, r_id, liked, voted_on=datetime.now()):
        self.uni = uni
        self.r_id = r_id
        self.liked = liked
        self.voted_on = voted_on

    def save(self):
        db.engine.execute('INSERT INTO votes VALUES (%s, %s, %s, %s)', (self.uni, self.r_id, self.voted_on, self.liked))

    @staticmethod
    def find(uni, rid):
        cur = db.engine.execute('SELECT * FROM votes v WHERE v.uni = %s AND v.r_id = %s', (uni, rid))

        if cur.rowcount == 0:
            return None

        (uni, r_id, voted_on, liked) = cur.fetchone()
        cur.close()
        return Vote(uni, r_id, liked, voted_on)


class Review(object):
    def __init__(self, c_id, uni, t_uni, general, workload, sentiment_score=0, written_on=datetime.now(), r_id=None):
        self.c_id = c_id
        self.uni = uni
        self.t_uni = t_uni
        self.general = general
        self.workload = workload
        self.sentiment_score = sentiment_score
        self.written_on = written_on
        self.r_id = r_id

    def save(self):
        db.engine.execute('''
            INSERT INTO reviews (c_id, uni, teacher_uni, general_content, workload_content, sentiment_score, written_on)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (self.c_id, self.uni, self.t_uni, self.general, self.workload, self.sentiment_score, self.written_on))

    def get_teacher(self):
        cur = db.engine.execute('SELECT * FROM teachers t WHERE t.uni = %s', (self.t_uni, ))

        if cur.rowcount == 0:
            return None
        t = Teacher(*next(cur))
        cur.close()
        return t

    def get_course(self):
        cur = db.engine.execute('SELECT * FROM courses c WHERE c.c_id = %s', (self.c_id))

        if cur.rowcount == 0:
            return None

        c = Course(*next(cur))
        cur.close()
        return c

    def get_votes(self):
        cur = db.engine.execute('SELECT COUNT(*) FROM votes v WHERE v.r_id = %s AND liked = TRUE', (self.r_id,))
        agree = 0 if cur.rowcount == 0 else cur.fetchone()[0]

        cur = db.engine.execute('SELECT COUNT(*) FROM votes v WHERE v.r_id = %s AND liked = FALSE', (self.r_id,))
        disagree = 0 if cur.rowcount == 0 else cur.fetchone()[0]
        cur.close()

        return agree, disagree

    @staticmethod
    def review_generator(cur):
        for (r_id, c_id, uni, t_uni, g_content, w_content, s_score, written_on) in cur:
            yield Review(c_id, uni, t_uni, g_content, w_content, s_score, written_on, r_id)

        cur.close()

    @staticmethod
    def find(val, field='r_id'):
        query = '''SELECT * FROM reviews WHERE {} = %s ORDER BY written_on DESC'''.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        return Review.review_generator(cur)


class Department(object):
    def __init__(self, did, name, abbrev):
        self.did = did
        self.name = name
        self.abbrev = abbrev

    def save(self):
        db.engine.execute('INSERT INTO departments VALUES (%s, %s)', (self.did, self.name, self.abbrev))

    def get_courses(self):
        cur = db.engine.execute('''SELECT c.c_id, c.name, c.abbrev FROM courses c, course_department d 
                                   WHERE c.c_id = d.c_id AND d.d_id = %s
                                ''', (self.did, ))

        if cur.rowcount == 0:
            return None

        return Course.courses_generator(cur)

    def get_teachers(self):
        cur = db.engine.execute(
            ''' SELECT t.uni, t.name 
                FROM teachers t, teachers_department d
                WHERE d.d_id = %s AND t.uni = d.uni
                ORDER BY t.name ASC
            ''', (self.did,))

        if cur.rowcount == 0:
            return None
        return Teacher.teacher_generator(cur)

    @staticmethod
    def department_generator(cur):
        for (did, name, abbrev) in cur:
            yield Department(did, name, abbrev)

        cur.close()

    @staticmethod
    def find(val, field='d_id'):
        query = 'SELECT * FROM departments WHERE {} = %s'.format(field)
        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        return Department.department_generator(cur)

    @staticmethod
    def find_all():
        cur = db.engine.execute('SELECT * FROM departments')

        if cur.rowcount == 0:
            return None

        return Department.department_generator(cur)

    @staticmethod
    def search(query):
        cur = db.engine.execute('SELECT * FROM departments WHERE LOWER(name) LIKE LOWER(%s)', (query,)
                                )
        if cur.rowcount == 0:
            return None

        return Department.department_generator(cur)


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
            cur = db.engine.execute('SELECT t.c_id FROM teaches t WHERE t.uni = %s', (self.uni, ))
            self.courses = [next(Course.find(cid)) for (cid,) in cur]

        return self.courses

    def get_reviews(self):
        return Review.find(self.uni, 'teacher_uni')

    def get_departments(self):
        if not self.departments:
            cur = db.engine.execute('SELECT td.d_id FROM teachers_department td WHERE td.uni = %s', (self.uni,))
            self.departments = [next(Department.find(did)) for (did,) in cur]
        return self.departments

    @staticmethod
    def teacher_generator(cur):
        for (uni, name) in cur:
            yield Teacher(uni, name)

        cur.close()

    @staticmethod
    def search(query):
        cur = db.engine.execute('SELECT * FROM teachers WHERE LOWER(name) LIKE %s OR LOWER(uni) LIKE %s', (query, query))

        if cur.rowcount == 0:
            return None
        return Teacher.teacher_generator(cur)

    @staticmethod
    def find(val, field='uni'):
        query = 'SELECT * FROM teachers WHERE {} = %s'.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        return Teacher.teacher_generator(cur)


class Course(object):
    def __init__(self, c_id, name, abbrev, departments=None, teachers=None):
        self.c_id = c_id
        self.name = name
        self.abbrev = abbrev
        self.departments = []
        self.teachers = []
        self.reviews = []

        if type(departments) == list:
            for d in departments:
                if type(d) != Department:
                    raise TypeError('input list departments must all be of type Department')

            self.departments = departments
        elif type(departments) == Department:
            self.departments.append(departments)
        elif departments:
            # allow for departments to be None
            raise TypeError('input departments must be of type Department or list of Department')

        if type(teachers) == list:
            for t in teachers:
                if type(t) != Teacher:
                    raise TypeError('input list teachers must all be of type Teacher')

            self.teachers = teachers
        elif type(teachers) == Teacher:
            self.teachers.append(teachers)
        elif teachers:
            # allow for teachers to be None
            raise TypeError('input teachers must be of type Teacher or list of Teacher')

    def get_departments(self):
        if not self.departments:
            cur = db.engine.execute('SELECT cd.d_id FROM course_department cd WHERE cd.c_id = %s', (self.c_id, ))
            self.departments = [next(Department.find(did)) for (did,) in cur]
        return self.departments

    def get_teachers(self):
        if not self.teachers:
            cur = db.engine.execute('SELECT ts.uni FROM teaches ts WHERE ts.c_id = %s ', (self.c_id,))
            self.teachers = [next(Teacher.find(uni)) for (uni,) in cur]
            cur.close()
        return self.teachers

    def get_reviews(self):
        return Review.find(self.c_id, 'c_id')

    @staticmethod
    def courses_generator(cur):
        for (c_id, name, abbrev) in cur:
            yield Course(c_id, name, abbrev)

        cur.close()

    @staticmethod
    def find(val, field='c_id'):
        query = 'SELECT * FROM courses WHERE {} = %s'.format(field)

        cur = db.engine.execute(query, (val,))

        if cur.rowcount == 0:
            return None

        return Course.courses_generator(cur)


    @staticmethod
    def search(query):
        cur = db.engine.execute(
            '''SELECT c.c_id, c.name, c.abbrev
               FROM courses c, course_department d
               WHERE LOWER(c.name) LIKE LOWER(%s)
               AND c.c_id = d.c_id
               ORDER BY d.d_id, c.name ASC 
               ''', (query,))
        if cur.rowcount == 0:
            return None

        return Course.courses_generator(cur)
