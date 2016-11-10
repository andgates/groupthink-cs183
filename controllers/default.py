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
    """
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
                username=auth.user.username,
                addtl_info=auth.user.addtl_info,
                skills=auth.user.skills,
                enrolled_courses=auth.user.enrolled_courses
            )
    """

    ## Redirect the user to their enrolled courses page upon log in
    redirect(URL('default', 'enrolled_courses'))

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
        form.add_button('Cancel', URL('enrolled_courses'))
    else:
        # If there are arguments, edit a course
        q = ((db.course.admin_email == auth.user.email) &
                (db.course.id == request.args(0)))
        # Get course record
        course = db(q).select().first()
        # Invariant: Check if project exists
        if course is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'enrolled_courses'))

        args = request.args(0)
        form = SQLFORM(db.course, course, deletable=True, showid=False)
        form.add_button('Cancel', URL('enrolled_courses'))

    if form.process().accepted:
        session.flash = T('Course created' if args is None else 'Course edited')
        redirect(URL('default', 'enrolled_courses'))

    return dict(args=args,form=form)

@auth.requires_login()
def enrolled_courses():

    courses = db(db.course).select()
    students = db(db.auth_user).select()

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
    # bool used to track valid course ids
    valid = None
    # form factory allows us to take in a variable without creating
    # essentially a temp field
    form = SQLFORM.factory(
        Field('course_id', requires=IS_NOT_EMPTY()))

    if form.process().accepted:
        # create iterable objects of the dbs
        courses = db(db.course).select()
        students = db(db.auth_user).select()
        # check courses first so we can jump out if its not a real course
        for c in courses:
            # check is the course is equal to a valid course
            if c.course_id == form.vars.course_id:
                # check if there are students, because cant append to none
                if c.enrolled_students:
                    # check if the user is already in the course
                    if auth.user.email in c.enrolled_students:
                        # the user is in the class we can jump back to courses
                        session.flash = "Already Enrolled"
                        redirect(URL('default','join'))
                        break
                    else:
                        # not in the course and courses isn't empty then we use append
                        c.enrolled_students.append(auth.user.email)
                        c.update_record()
                else:
                    # enrolled students was empty so the user cant be in the class
                    # the list was empty so you =  instead of append
                    c.enrolled_students = auth.user.email
                    c.update_record()
                # the course is real change the validator
                valid = True

        # only handle linking to the student if the course is real
        if valid:
            # similiar to course find the student and add course to their list of enrolled courses
            # use the same = and append functions. Jump back to courses when complete
            for d in students:
                if d.email == auth.user.email:
                    if d.enrolled_courses:
                        d.enrolled_courses.append(form.vars.course_id)
                        d.update_record()
                        session.flash = "Class Joined"
                        redirect(URL('default', 'enrolled_courses'))
                    else:
                        d.enrolled_courses = form.vars.course_id
                        d.update_record()
                        session.flash = "Class Joined"
                        redirect(URL('default', 'enrolled_courses'))
        # if the course wasnt valid flash and reload the join page
        else:
            session.flash = "Course Not Found"
            redirect(URL('default', 'join'))
    return dict(form=form)

@auth.requires_login()
def project_list():
    """
    This is the project list controller.

    Returns: A dictionary of projects and associated info for a given course_id.
    """

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
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
def project():

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Extract course_id,project_id from url argument (Button on individual project)
        course_id, project_id = request.args[:2]
        # Query database for project with correct course_id
        project = db(db.project.course_id == course_id and db.project.id == project_id).select().first()

        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

        # Matching Algorithm
        students = db(db.auth_user).select()
        matchingStudents = []
        # get a list of students
        for i in students:
            # is this student in the course the projects in
            # This checks to make sure the user is enrolled in at least one course
            # Otherwise 'if course_id in i.enrolled_courses' will through an error
            if i.enrolled_courses:
                if course_id in i.enrolled_courses:
                    # loop throught the skils
                    # we have to check case so simple query doesnt work
                    for j in project.needed_skills:
                        # check this person even has skills
                        if i.skills:
                            # loop through those skills
                            for k in i.skills:
                                # compare the skill in lowercase, so its not case sensitive
                                if j.lower() == k.lower():
                                    # check that the student isnt already counted
                                    if i not in matchingStudents:
                                        # add the student
                                        matchingStudents.append(i)

    return dict(p=project,get_user_name_from_email=get_user_name_from_email,
        course_id=course_id,course_name=course_name, matches=matchingStudents)

@auth.requires_login()
def edit_project():
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
        form.add_button('Cancel', URL('project_list', args=course_id))
    else:
        # If there are arguments, edit a project
        q = ((db.project.user_email == auth.user.email) &
                (db.project.id == project_id))
        # Get project record
        project = db(q).select().first()
        # Invariant: Check if project exists
        if project is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'project_list', args=course_id))

        form = SQLFORM(db.project, project, deletable=True, showid=False)
        form.vars.course_id = course_id
        form.add_button('Cancel', URL('project_list', args=course_id))

    if form.process().accepted:
        session.flash = T('Project created' if project_id is None else 'Project edited')
        redirect(URL('default', 'project_list', args=course_id))

    return dict(form=form,args=args)

@auth.requires_login()
def profile():

    args = request.args(0)

    current_profile = db(db.auth_user.username == args).select().first()

    # Query for projects made by user
    projects = db(db.project.user_email == current_profile.email).select()


    return dict(current_profile=current_profile,projects=projects,get_user_name_from_email=get_user_name_from_email)

@auth.requires_login()
def members():

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Extract the course_id from the argument ("View Course Members" button in project.html)
        course_id = request.args(0)
        # Get the course name for displaying on the webpage
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name
        # Query all students. (This is really inefficient but I see no way to get just the students enrolled in a given course)
        students = db(db.auth_user).select()
        members = []
        for s in students:
            # Invariant, if a student has no courses, enrolled_courses will not be iterable
            if s.enrolled_courses == None:
                pass
            # Add the students that are enrolled in the current course
            elif course_id in s.enrolled_courses:
                members.append(s)


    return dict(members=members,get_user_name_from_email=get_user_name_from_email,course_name=course_name)


def redirect_after_signup(form):
    redirect(URL('default', 'index'))

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

    return dict(form=auth())

@auth.requires_login()
def statistics():
    course_id = request.args(0)
    if course_id is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Query database for project with correct course_id
        students = db(db.auth_user).select()
        members = []
        for s in students:
            # Invariant, if a student has no courses, enrolled_courses will not be iterable
            if s.enrolled_courses == None:
                pass
            # Add the students that are enrolled in the current course
            elif course_id in s.enrolled_courses:
                members.append(s)

        projects = db(db.project.course_id == course_id).select()



        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        #course_name = course.course_name


    return dict(p = projects, members = members, course = course)


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
