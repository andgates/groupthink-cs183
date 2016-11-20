# -*- coding: utf-8 -*-

"""
GroupThink™

"""


# ---s is the default controller for Grputhink
# - index is the default action of any application
# - user is required for authentication and authorizati
# Built in modules
import json, random, string

__author__ = "Sean Dougher, Savanna Jordan, Ryan Monroe, and Michael Gates"
__email__ = "mjgates@ucsc.edu"
__version__ = "0.011111"
__status__ = "Development"
__date__ = "11/19/2016"

##### Make this a function
"""
        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name
"""


def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""

    #gets the user based on user email
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        #if there is no name, returns none
        return 'None'
    else:
        #otherwise, returns first and last name
        return ' '.join([u.first_name, u.last_name])

def index():
    """
    Index is the dashboard for logged in users.
    """

    current_profile = None

    #Current user logged in
    if auth.user:
        current_profile = db(db.auth_user.email == auth.user.email).select().first()


    #TODO @Michael: Create my projects list


    #Returns a dict containing the current profile
    return dict(current_profile=current_profile)

@auth.requires_login()
#adds ability to edit course
def edit_course():
    """
    This is the page to create / edit / delete a course.
    """

    args = None                             #Args = arguments
    form = None                             #form = form that user interacts with

    # Create a new course if there are no arguments
    if request.args(0) is None:
        #Creates a new form using the course database
        form = SQLFORM(db.course)
        #adds a cancel button to return
        form.add_button('Cancel', URL('enrolled_courses'))
    # If there are arguments, edit a course
    else:
        #Queries for user that matches admin email, and is enrolled in a specific course
        q = ((db.course.admin_email == auth.user.email) and
                (db.course.id == request.args(0)))
        # Get course record
        course = db(q).select().first()
        # Invariant: Check if project exists
        if course is None:
            #User is not authorized
            session.flash = T('Not Authorized')
            redirect(URL('default', 'enrolled_courses'))

        args = request.args(0)
        form = SQLFORM(db.course, course, deletable=True, showid=False)
        form.add_button('Cancel', URL('enrolled_courses'))

    if form.process().accepted:
        # query for the new course
        newCourse = db(db.course.course_id == form.vars.course_id).select().first()
        # query the user(admin)
        admin = db(db.auth_user.email == auth.user.email).select().first()
        # add the new course to the admins enrolled courses
        # Check to see if the student is enrolled in at least one course
        if admin.enrolled_courses:
            # If the admin is already in the course, they must be editing.
            if newCourse.id in admin.enrolled_courses:
                # @TODO: Update to insert_or_update()
                # Don't add anything to enrolled_courses
                pass
            # The admin isn't enrolled in this course, add them
            else:
                admin.enrolled_courses.append(newCourse)
                admin.update_record()
        else:
            #Otherwise, they are enrolled in this course
            admin.enrolled_courses = newCourse
            admin.update_record()
        session.flash = T('Course created' if args is None else 'Course edited')
        redirect(URL('default', 'enrolled_courses'))

    return dict(args=args,form=form)

@auth.requires_login()
#Displays all enrolled courses to the current user
def enrolled_courses():

    #TODO: Michael
    # Updated:
    # my_courses = db(db.course.course_id.contains(db.auth_user.enrolled_courses)).select()
    # list_my_courses = [c for c in my_courses]

    #Gets the courses from the course database
    courses = db(db.course).select()
    #Gets the current user
    student = db(db.auth_user.email == auth.user.email).select().first()

    return dict(courses=courses, student=student)

"""
# Believe I made this obsolete
def courseVerification(course_id):
    courses = db(db.course).select()
    res = None
    for c in courses:
        if c.course_id == course_id:
            res=True
    return dict(res=res)
"""

@auth.requires_login()
#Allows user to join a course
def join():
    # form factory allows us to take in a variable without creating
    # essentially a temp field
    form = SQLFORM.factory(
        Field('course_id', requires=IS_NOT_EMPTY()))

    #returns iterable course object
    courses = db(db.course).select()
    #returns iterable student object
    students = db(db.auth_user).select()

    #TODO: Update studentReference to use one query to check if student is already enrolled
    #TODO: Look into how difficult it will be to add an enrollment table

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
                #loops through enrolled courses, finding matching course_id
                for i in studentReference.enrolled_courses:
                    if i.course_id == form.vars.course_id:
                        #if user is already enrolled...
                        session.flash = "Already Enrolled"
                        # this will redirect the page and break out of the whole function
                        redirect(URL('default', 'enrolled_courses'))
                # must append if the list isnt empty
                studentReference.enrolled_courses.append(selectedCourse)
                studentReference.update_record()
            else:
                # if the list is empty, set the enrolled course to the selected course
                studentReference.enrolled_courses = selectedCourse
                studentReference.update_record()
            # after adding to the student, add the student to the course
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
#Displays list of current projects to user
def project_list():
    """
    This is the project list controller.

    Displays list of projects for a give course

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

        #TODO: CALL FUNCTION BELOW
        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

    return dict(projects=projects,get_user_name_from_email=get_user_name_from_email,
        course_id=course_id,course_name=course_name)

@auth.requires_login()
#Displays project information to user
def project():
    """
    Gets project information and displays to user
    """

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Extract course_id,project_id from url argument (Button on individual project)
        course_id, project_id = request.args[:2]
        # Query database for project with correct course_id
        project = db(db.project.course_id == course_id and db.project.id == project_id).select().first()

        #TODO: CALL FUNCTION BELOW:
        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

        # List to store matching student objects
        matchingStudents = []

        # Great way to efficiently query database
        # Query database for students enrolled in current course that also have at least one skill needed
        # A "rows" object is returned that contains all students in the course, with any of the needed skills
        students = db(db.auth_user.enrolled_courses.contains(course.id) and db.auth_user.skills.contains(project.needed_skills)).select()

        # This is just adding each "student" row object to a regular list, using list comprehension
        matchingStudents = [s for s in students]

    return dict(p=project,get_user_name_from_email=get_user_name_from_email,
        course_id=course_id,course_name=course_name, matches=matchingStudents)

def member_validation(form):
    """
    Function to make sure a user is in the database, given an email
    """
    unknown_emails = []

##########################################
#Update: include contains instead of a for loop

    this_project = form.vars.id

    #only one argument, being a string
    if type(form.vars.current_members) == str:
        #user exists
        if db(db.auth_user.email == form.vars.current_members).select().first():
            pass
        #user does not exist, output error to user
        else:
            form.errors.current_members = form.vars.current_members + " does not exist"
    else:
        #loops through all emails in database
        for email in form.vars.current_members:
            # Check to see if the email is in the auth_user database
            if db(db.auth_user.email == email).select().first():
                # The user was there, no wories man :'(
                pass

            else:
                #outputs each email that was not found in the database
                unknown_emails.append(email)
                unknown_string = ""
                ### if there's only one unkown email, skip the for loop
                for unknown in unknown_emails:
                    unknown_string = unknown_string + ", " + unknown
                form.errors.current_members = unknown_string + " not found."



@auth.requires_login()
#Allows user to edit project information
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
        this_project = db(db.project.id == form.vars.id).select().first()
        # There was only one user email entered
        if type(form.vars.current_members) == str:
            # Get the one user entered
            the_user = db(db.auth_user.email == form.vars.current_members).select().first()
            print("The User:", the_user)
            # Check if the user has at least one project
            if the_user.my_projects:
                # If the user is already in the project, they must be editing.
                if this_project.id in the_user.my_projects:
                    # @TODO: Update to insert_or_update()
                    # Don't add anything to my_projects
                    pass
                # The user isn't already in this project, add them
                else:
                    the_user.my_projects.append(this_project)
                    the_user.update_record()
            else:
                # Otherwise, this is thier first project
                the_user.my_projects = this_project
                the_user.update_record()
        # Multiple emails entered
        else:
            for email in form.vars.current_members:
                # Check to see if the email is in the auth_user database
                if db(db.auth_user.email == email).select().first():
                    # Get the one user entered
                    the_user = db(db.auth_user.email == email).select().first()
                    # Check if the user has at least one project
                    if the_user.my_projects:
                        # If the user is already in the project, they must be editing.
                        if this_project.id in the_user.my_projects:
                            # @TODO: Update to insert_or_update()
                            # Don't add anything to my_projects
                            pass
                        # The user isn't already in this project, add them
                        else:
                            the_user.my_projects.append(this_project)
                            the_user.update_record()
                    else:
                        # Otherwise, this is thier first project
                        the_user.my_projects = this_project
                        the_user.update_record()

        session.flash = T('Project created' if project_id is None else 'Project edited')
        redirect(URL('default', 'project', args=[course_id,form.vars.id]))

    return dict(form=form,args=args)

@auth.requires_login()
#displays profile to user
def profile():

    args = request.args(0)

    #gets current user's profile
    current_profile = db(db.auth_user.username == args).select().first()

    # Query for projects made by user
    projects = db(db.project.user_email == current_profile.email).select()


    return dict(current_profile=current_profile,projects=projects,get_user_name_from_email=get_user_name_from_email)

@auth.requires_login()
#displays membersbps
def members():

    current_user = db(db.auth_user.id == auth.user.id).select().first()

    if request.args(0) is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # Extract the course_id from the argument ("View Course Members" button in project.html)
        course_id = request.args(0)

        #TODO: CALL EXTRACT NAME FUNCTIONEE AL:OODO# Get the course name for displaying on the webpage
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

        # Que?™eries for all members in a given course
        rows_members = db(db.auth_user.enrolled_courses.contains(course.id)).select()

        # The ol' toss em'in a list ♪
        members = [m for m in rows_members]

        # Queries for members­ that have matching previous coursework (people who have taken the same class in the past)
        rows_coursework = db(db.auth_user.enrolled_courses.contains(course.id)
                            and db.auth_user.coursework.contains(current_user.coursework)).select()

        # Toss em' in a list ♫
        coursework_members = [m for m in rows_coursework]


    return dict(members=members,get_user_name_from_email=get_user_name_from_email,
                course_name=course_name,course_id=course_id,coursework_members=coursework_members)

#Built-in function for web2py, that does something
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

    return dict(form=auth())

@auth.requires_login()
#Displays various statistics to admin
def statistics():
    course_id = request.args(0)
    if course_id is None:
        session.flash = T('No course selected')
        redirect(URL('default', 'enrolled_courses'))
    else:
        # find the course
        course = db(db.course.course_id == course_id).select().first()

        members = []

        # Que?™eries for all members in a given course
        rows_members = db(db.auth_user.enrolled_courses.contains(course.id)).select()

        members = [m for m in rows_members]

        #rows_not_in = db(db.auth_user.enrolled_courses.contains(course.id) and
        #not db.project.curent_members.contains(auth_user.email))

        project_ids = []
        # get the projects for the course
        projects = db(db.project.course_id == course_id).select()
        for p in projects:
            project_ids.append(p.id)

        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        #course_name = course.course_name

        rows_in_projects = db(db.auth_user.enrolled_courses.contains(course.id) and db.auth_user.my_projects.contains(project_ids)).select()

        in_projects = [n for n in rows_in_projects]

        not_in_projects = []

        for m in members:
            if m not in in_projects:
                not_in_projects.append(m)


    return dict(p = projects, members = members, course = course,not_in_projects=not_in_projects)


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
