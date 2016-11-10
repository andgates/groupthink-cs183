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
    Index is only used to verify if a user is in the student database currently.
    """

    # Checks to see if the user is in the student database, adds them if needed.
    if auth.user:
        res = False
        email = db(db.student.user_email == auth.user.email).select()
        if email:
            res = True
        if (res != True):
            db.student.insert(
                first_name = auth.user.first_name,
                last_name = auth.user.last_name,
                user_email=auth.user.email,
            )

    ## Redirect the user to their enrolled courses page upon log in
    redirect(URL('default', 'course'))

    ## We should also redirect a new user to the edit profile page once that is setup

    return dict()

@auth.requires_login()
def edit_course():
    """
    This is the page to create / edit / delete a course.
    """
    args = None
    form = None

    if request.args(0) is None:
        # Create a new course if there are no arguments
        form = SQLFORM(db.course)
        form.add_button('Cancel', URL('course'))
    else:
        # If there are arguments, edit a course
        q = ((db.course.admin_email == auth.user.email) &
                (db.course.id == request.args(0)))
        # Get course record
        course = db(q).select().first()
        # Invariant: Check if project exists
        if course is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'course'))

        args = request.args(0)
        form = SQLFORM(db.course, course, deletable=True, showid=False)
        form.add_button('Cancel', URL('course'))

    if form.process().accepted:
        session.flash = T('Course created' if args is None else 'Course edited')
        redirect(URL('default', 'course'))

    return dict(args=args,form=form)

@auth.requires_login()
def course():

    courses = db(db.course).select()
    students = db(db.student).select()

    return dict(courses=courses, students=students)

def courseVerification(course_id):
    courses = db(db.course).select()
    res = None
    for c in courses:
        if c.course_id == course_id:
            res=True
    return dict(res=res)

@auth.requires_login()
def join():
    valid = None
    form = SQLFORM.factory(
        Field('course_id', requires=IS_NOT_EMPTY()))

    if form.process().accepted:
        courses = db(db.course).select()
        students = db(db.student).select()
        for c in courses:
            if c.course_id == form.vars.course_id:
                if c.enrolled_students:
                    if auth.user.email in c.enrolled_students:
                        session.flash = "Already Enrolled"
                        redirect(URL('default','join'))
                        break
                    else:
                        c.enrolled_students.append(auth.user.email)
                        c.update_record()
                else:
                    c.enrolled_students = auth.user.email
                    c.update_record()
                valid = True

        if valid:
            for d in students:
                if d.user_email == auth.user.email:
                    if d.enrolled_courses:
                        d.enrolled_courses.append(form.vars.course_id)
                        d.update_record()
                        session.flash = "Class Joined"
                        redirect(URL('default', 'course'))
                    else:
                        d.enrolled_courses = form.vars.course_id
                        d.update_record()
                        session.flash = "Class Joined"
                        redirect(URL('default', 'course'))
        else:
            session.flash = "Course Not Found"
            redirect(URL('default', 'join'))
    return dict(form=form)

@auth.requires_login()
def project():
    """
    This is the project controller.

    Returns: A dictionary of projects and associated user names.
    """

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'course'))
    else:
        # Extract course_id from url argument (Button on enrolled_courses page)
        course_id = request.args(0)
        # Query database for all projects with correct course_id
        projects = db(db.project.course_id == course_id).select(orderby=~db.project.created_on)

        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

    # Gets a list of the 20 most recent projects, orders by date created
    #projects = db(db.project).select(orderby=~db.project.created_on, limitby=(0,20))

    return dict(projects=projects,get_user_name_from_email=get_user_name_from_email,
        course_id=course_id,course_name=course_name)


@auth.requires_login()
def edit():
    """
    This is the page to create / edit / delete a project.
    """
    form = None
    args = None

    # Get the arguments from the URL request
    args = request.args

    # If there is only one argument (course_id), then we are creating a post
    if len(args) == 1:
        new_post = True
        # Extract the first entry in the args list
        course_id = args(0)
        project_id = None
    # Otherwise, we're editing a project. Extract post id and course_id
    else:
        new_post = False
        course_id, project_id = request.args[:2]

    if new_post:
        # Create a new project if there are no arguments
        form = SQLFORM(db.project)
        # Fill the course_id field with the current course_id
        form.vars.course_id = course_id
        form.add_button('Cancel', URL('project', args=course_id))
    else:
        # If there are arguments, edit a project
        q = ((db.project.user_email == auth.user.email) &
                (db.project.id == project_id))
        # Get project record
        project = db(q).select().first()
        # Invariant: Check if project exists
        if project is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'project', args=course_id))

        form = SQLFORM(db.project, project, deletable=True, showid=False)
        form.vars.course_id = course_id
        form.add_button('Cancel', URL('project', args=course_id))

    if form.process().accepted:
        session.flash = T('Project created' if project_id is None else 'Project edited')
        redirect(URL('default', 'project', args=course_id))

    return dict(form=form,args=args)

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

    # A messy fix for using student table separate from auth
    # Users weren't getting added to the student table because they didn't always visit index.html after signup
    auth.settings.register_onaccept = redirect_after_signup

    return dict(form=auth(), get_user_name_from_email=get_user_name_from_email)

def redirect_after_signup(form):
    redirect(URL('default', 'index'))

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

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'course'))
    else:
        # Extract the course_id from the argument ("View Course Members" button in project.html)
        course_id = request.args(0)
        # Get the course name for displaying on the webpage
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name
        # Query all students. (This is really inefficient but I see no way to get just the students enrolled in a given course)
        students = db(db.student).select()
        members = []
        for s in students:
            # Invariant, if a student has no courses, enrolled_courses will not be iterable
            if s.enrolled_courses == None:
                pass
            # Add the students that are enrolled in the current course
            elif course_id in s.enrolled_courses:
                members.append(s)


    return dict(members=members,get_user_name_from_email=get_user_name_from_email,course_name=course_name)
