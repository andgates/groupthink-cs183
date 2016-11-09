# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

import json
import random, string

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def index():
    """
    This is the main controller.
    """

    if auth.user:
        res = False
        email = db(db.student.user_email == auth.user.email).select()
        if email:
            res = True
        if (res != True):
            db.student.insert(
                user_email=auth.user.email,
            )
    return dict()

@auth.requires_login()
def edit_course():
    """
    This is the page to create / edit / delete a project.
    """
    args = None
    form = None

    if request.args(0) is None:
        # Create a new project if there are no arguments
        form = SQLFORM(db.course)
        form.add_button('Cancel', URL('course'))
    else:
        # If there are arguments, edit a project
        q = ((db.course.admin_email == auth.user.email) &
                (db.course.id == request.args(0)))
        # Get project record
        project = db(q).select().first()
        # Invariant: Check if project exists
        if project is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'project'))

        args = request.args(0)
        form = SQLFORM(db.course, project, deletable=True, showid=False)
        form.add_button('Cancel', URL('course'))

    if form.process().accepted:
        session.flash = T('Course created' if args is None else 'Course edited')
        redirect(URL('default', 'course'))

    return dict(args=args,form=form)

    return dict(form=form)

@auth.requires_login()
def course():

    courses = db(db.course).select()
    students = db(db.student).select()

    return dict(courses=courses, students=students)

@auth.requires_login()
def student():

    students = db(db.student).select()

    return dict(students=students)

def join_validation(form):
    q = form.vars.enrolled_courses == db.course.course_id

    course = db(q).select().first()

    if course is None:
        form.errors.enrolled_courses = "Course does not exist"

@auth.requires_login()
def join():
#    update = db.course(request.args(0))
#    form = SQLFORM(db.course, update)
    test = "FUCK"
    form = SQLFORM.factory(
        Field('course_id', requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        email = db(db.course).select()
        for c in email:
            if c.course_id == form.vars.course_id:
                c.enrolled_students.append(auth.user.email)
                c.update_record()
    else:
        test = "SUPER FUCK"

    return dict(form=form, test=test)
#    #if form.process(onvalidation=join_validation).accepted:
#    email = db(db.course.course_id == db.student.enrolled_courses and db.student.user_email == auth.user.email).select().first()
#    courses = db(db.course.course_id == db.student.enrolled_courses).select().first()
#    if courses:
#        courses.enrolled_students=email.user_email
#        courses.update_record()
#    session.flash = "Class Joined"





@auth.requires_login()
def project():
    """
    This is the project controller.

    Returns: A dictionary of projects and associated user names.
    """


    # Gets a list of the 20 most recent projects, orders by date created
    projects = db(db.project).select(orderby=~db.project.created_on, limitby=(0,20))

    return dict(projects=projects,get_user_name_from_email=get_user_name_from_email)


@auth.requires_login()
def edit():
    """
    This is the page to create / edit / delete a project.
    """
    args = None
    form = None

    if request.args(0) is None:
        # Create a new project if there are no arguments
        form = SQLFORM(db.project)
        form.add_button('Cancel', URL('project'))
    else:
        # If there are arguments, edit a project
        q = ((db.project.user_email == auth.user.email) &
                (db.project.id == request.args(0)))
        # Get project record
        project = db(q).select().first()
        # Invariant: Check if project exists
        if project is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'project'))

        args = request.args(0)
        form = SQLFORM(db.project, project, deletable=True, showid=False)
        form.add_button('Cancel', URL('project'))

    if form.process().accepted:
        session.flash = T('Project created' if args is None else 'Project edited')
        redirect(URL('default', 'project'))

    return dict(args=args,form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """



    return dict(form=auth(), get_user_name_from_email=get_user_name_from_email)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()



@auth.requires_login()
def members():

    members=db(db.course)
    #numStudents=db(db.course.numStudents)
    #members = db(db.course).select(course.en)....

    #members="class members";

    return dict(members=members,get_user_name_from_email=get_user_name_from_email)