# -*- coding: utf-8 -*-

"""
GroupThink™

Interfaces with Javascript via AJAX calls

"""

# Built in modules
import json, random, string, requests, traceback

__author__ = "Sean Dougher, Savanna Jordan, Ryan Monroe, and Michael Gates"
__email__ = "mjgates@ucsc.edu, sjdoughe@ucsc.edu, srjordan@ucsc.edu, rmonroe@ucsc.edu"
__version__ = "1"
__status__ = "Release"
__date__ = "11/23/2016"


"""
Gets a list of a users enrolled courses, in response to a AJAX call
in Javascript, served to my_courses.html
"""
@auth.requires_login()
def get_my_courses():

    # # Gets the current user
    student = db(db.auth_user.email == auth.user.email).select().first()
    # admin = student.email
    # Gets all the courses oh god
    courses = db(db.course).select()

    current_url = URL('default', 'edit_course')
    stat_url = URL('default','statistics')

    my_courses = []

    # Nonetype check to ensure user is enrolled in at least one course
    if student.enrolled_courses:
        for c in courses:
            # Only appends teh courses that the current student is in
            if c.id in student.enrolled_courses:
                my_courses.append(c)



    return response.json(dict(my_courses=my_courses, current_url=current_url, stat_url = stat_url))

"""
Gets a list of a projects
"""
@auth.requires_login()
def get_projects():
    projects = None
    course_id = request.vars.c_id.strip()
    if request.vars.c_id:

        # Query database for all projects with correct course_id
        projects = db(db.project.course_id == course_id).select(orderby=~db.project.created_on)



        current_url = URL('default', 'edit_project')



        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name





    return response.json(dict(projects=projects, current_url=current_url))

@auth.requires_login()
def get_members():

    members = None
    course_id = request.vars.c_id
    if request.vars.c_id:
        current_user = db(db.auth_user.id == auth.user.id).select().first()

        # Extract the course_id from the argument ("View Course Members" button in project.html)
        course_id = request.vars.c_id.strip()
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name
        # Que?™eries for all members in a given course
        rows_members = db(db.auth_user.enrolled_courses.contains(course.id)).select(orderby=~db.auth_user.id)

        # The ol' toss em'in a list ♪
        members = [m for m in rows_members]

        temp = members[:]
        for i in temp:
            if i.picture or i.picture_file:
                i.picture = ""
                i.picture_file = ""

        # # Queries for members­ that have matching previous coursework (people who have taken the same class in the past)
        # rows_coursework = db(db.auth_user.enrolled_courses.contains(course.id)
        #                      and db.auth_user.coursework.contains(current_user.coursework)).select()

        # Toss em' in a list ♫
        # coursework_members = [m for m in rows_coursework]

        profile_url = URL('default', 'profile')
        print (profile_url)
        print ("here")
        print "leaving"
    return response.json(dict(members=members, profile_url=profile_url))


def get_statistics():

    course=None;

    #course_id = request.vars.c_id.strip()

    if request.vars.c_id:
        # Query database for correct course object
        course = db(db.course.id == request.vars.c_id).select().first()

        if course.enrolled_students:
            members = [db(db.auth_user.id == m).select().first()
                       for m in course.enrolled_students if course.enrolled_students]
        else:
            members = None

        course_id= course.course_id;


        project_ids = []
        # get the projects for the course
        projects = db(db.project.course_id == course_id).select()
        for p in projects:
                project_ids.append(p.id)

        rows_in_projects = db(db.auth_user.enrolled_courses.contains(course.id) and db.auth_user.my_projects.contains(project_ids)).select()

        in_projects = [n for n in rows_in_projects]

        not_in_projects = []

        if members:
            for m in members:
                if m not in in_projects:
                    not_in_projects.append(m)

    return response.json(dict(course=course, course_members=members, projects_in_course=projects, not_in_projects=not_in_projects,))


"""
Gets a single project
"""
@auth.requires_login()
def get_one_project():

    project = None

    course_id = request.vars.c_id.strip()
    project_id = request.vars.p_id.strip()
    if request.vars.c_id and request.vars.p_id:

        # Query database for project with correct course_id
        project = db(db.project.course_id == course_id and db.project.id == project_id).select().first()

        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name
        # List to store matching student objects
        matchingStudents = []

        # Great way to efficiently query database
        # Query database for students enrolled in current course that also have at least one skill needed
        # A "rows" object is returned that contains all students in the course, with any of the needed skills
        students = db(db.auth_user.enrolled_courses.contains(course.id) & db.auth_user.skills.contains(
            project.needed_skills)).select()


        current_user = db(db.auth_user.email == auth.user.email).select().first()

        # Not sure in alg works for students. shows those not in course

        # filter the project for PO and members

        # This is just adding each "student" row object to a regular list, using list comprehension
        matchingStudents = [s for s in students]
        for i in matchingStudents:
            if (i.email == project.user_email):
                matchingStudents.remove(i)

        # filter the list of students for current members
        for i in matchingStudents:
            for j in project.current_members:
                if j == i.email:
                    matchingStudents.remove(i)

        matchingStudents = [s.username for s in matchingStudents]

    return response.json(dict(project=project, matches=matchingStudents,))


@auth.requires_login()
def edit_project():

    if request.vars.form == None:
        form = None
        form = SQLFORM(db.project)


    if  request.vars.form != None and request.vars.form.process().accepted:
        session.flash=T('PROJECT CREATED')
        redirect(URL('default','index'))
        # print("VERY NICE")

    return response.json(dict(form=form))
@auth.requires_login()
def get_current():
    student = db(db.auth_user.email == auth.user.email).select().first()
    current_user = student.email
    return response.json(dict(current_user=current_user))

