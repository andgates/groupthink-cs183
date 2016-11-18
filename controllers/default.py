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
    Index is the dashboard for logged in users.
    """

    current_profile = None

    if auth.user:
        current_profile = db(db.auth_user.email == auth.user.email).select().first()

    ## Redirect the user to their enrolled courses page upon log in
    #redirect(URL('default', 'enrolled_courses'))

    ## We should also redirect a new user to the edit profile page once that is setup

    return dict(current_profile=current_profile)

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
        # query the new course
        newCourse = db(db.course.course_id == form.vars.course_id).select().first()
        # query the user
        admin = db(db.auth_user.email == auth.user.email).select().first()
        # add the new course to the admins enrolled courses
        # Check to see if the student is enrolled in at least one course
        if admin.enrolled_courses:
            # If the admin is already in the course, they must be editing.
            if newCourse.id in admin.enrolled_courses:
                # Don't add anything to enrolled_courses
                pass
            # The admin isn't enrolled in this course, add them
            else:
                admin.enrolled_courses.append(newCourse)
                admin.update_record()
        else:
            admin.enrolled_courses = newCourse
            admin.update_record()
        session.flash = T('Course created' if args is None else 'Course edited')
        redirect(URL('default', 'enrolled_courses'))

    return dict(args=args,form=form)

@auth.requires_login()
def enrolled_courses():

    courses = db(db.course).select()
    student = db(db.auth_user.email == auth.user.email).select().first()

    return dict(courses=courses, student=student)

# Believe I made this obsolete
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

    # create iterable objects of the dbs
    courses = db(db.course).select()
    students = db(db.auth_user).select()

    # get a reference to the specific student
    studentReference = db(db.auth_user.email == auth.user.email).select().first()
    # this will hold the selected course. cant do here the query uses the form
    # so the form must be first accepted
    selectedCourse = ""

    if form.process().accepted:
        # run a query to see if the course exist
        selectedCourse = db(db.course.course_id == form.vars.course_id).select().first()
        #if the course exist
        if selectedCourse:
            # check if there are enrolled courses
            if studentReference.enrolled_courses:
                # before adding make sure that the course isnt there already
                # this is the only way i could get validation to work cannot just check for reference
                for i in studentReference.enrolled_courses:
                    if i.course_id == form.vars.course_id:
                        session.flash = "Already Enrolled"
                        # this will redirect the page and break out of the whole function
                        redirect(URL('default', 'enrolled_courses'))
                # must append if the list isnt empty
                studentReference.enrolled_courses.append(selectedCourse)
                studentReference.update_record()
            else:
                # if the list is empty use =
                studentReference.enrolled_courses = selectedCourse
                studentReference.update_record()
            # after adding to the student add, the student to the course
            if selectedCourse.enrolled_students:
                selectedCourse.enrolled_students.append(studentReference)
                selectedCourse.update_record()
            else:
                selectedCourse.enrolled_students = studentReference
                selectedCourse.update_record()
            # after adding go back to enrolled courses
            session.flash = "Course Joined"
            redirect(URL('default', 'enrolled_courses'))
        # query returned none, therefore the course doesnt exist
        else:
            session.flash = "Course Not Found"
            redirect(URL('default', 'join'))

    return dict(form=form, student=studentReference, course=selectedCourse)

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

        # Matching using reference
        matchingStudents = []
        # loop through references
        for d in course.enrolled_students:
            # find the student
            q = db(db.auth_user.id == d).select().first()
            # match sure the student has info
            if q:
                # loop through students skills
                for e in q.skills:
                    # loop through the projects skills
                    for f in project.needed_skills:
                        # do comparison in lowercase so not case sensitive
                        if f.lower() == e.lower():
                            # if the student isnt already counted add them
                            if q not in matchingStudents:
                                matchingStudents.append(q)

    return dict(p=project,get_user_name_from_email=get_user_name_from_email,
        course_id=course_id,course_name=course_name, matches=matchingStudents)


def member_validation(form):
    ugly_emails = []

    if type(form.vars.current_members) == str:
        if db(db.auth_user.email == form.vars.current_members).select().first():
            pass
        else:
            form.errors.current_members = form.vars.current_members + " does not exist"
    else:
        for email in form.vars.current_members:
            # Check to see if the email is in the auth_user database
            if db(db.auth_user.email == email).select().first():
                # That email was in the database, no worries man
                pass
            else:
                ugly_emails.append(email)
                ugly_string = ""
                for ugly in ugly_emails:
                    ugly_string = ugly_string + ", " + ugly
                form.errors.current_members = ugly_string + " not found."



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

    if form.process(onvalidation=member_validation).accepted:
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


def coursework_match(current_student, all_students):

    matchingStudents = []

    if current_student.coursework == None:
        return None

    for s_id in all_students:
        other_student = db(db.auth_user.id == s_id).select().first()
        if other_student:
            if other_student.coursework:
                for c in other_student.coursework:
                    for d in current_student.coursework:
                        if c.lower() == d.lower():
                            if other_student not in matchingStudents:
                                matchingStudents.append(other_student)

    return matchingStudents



@auth.requires_login()
def members():

    current_user = db(db.auth_user.id == auth.user.id).select().first()

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Extract the course_id from the argument ("View Course Members" button in project.html)
        course_id = request.args(0)
        # Get the course name for displaying on the webpage
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

        members = []
        # loops through the enrolled students and link the references to students
        for s in course.enrolled_students:
            q = db(db.auth_user.id == s).select().first()
            # add them to the list of members so we can pull there info
            members.append(q)

        coursework_members = coursework_match(current_user, course.enrolled_students)

    return dict(members=members,get_user_name_from_email=get_user_name_from_email,course_name=course_name,course_id=course_id,coursework_members=coursework_members)


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
        # find the course
        course = db(db.course.course_id == course_id).select().first()
        members = []
        # loops through the enrolled students and link the references to students
        for s in course.enrolled_students:
            q = db(db.auth_user.id == s).select().first()
            # add them to the list of members so we can pull there info
            members.append(q)
        # get the projects for the course
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
