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

    # Gets the current user
    student = db(db.auth_user.email == auth.user.email).select().first()

    # Gets all the courses oh god
    courses = db(db.course).select()

    my_courses = []

    for c in courses:
        # Only appends teh courses that the current student is in
        if c.id in student.enrolled_courses:
            my_courses.append(c)

    return response.json(dict(my_courses=my_courses))

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

        # Extract course name for webpage heading
        course = db(db.course.course_id == course_id).select().first()
        course_name = course.course_name

    return response.json(dict(projects=projects))

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
        students = db(db.auth_user.enrolled_courses.contains(course.id) and db.auth_user.skills.contains(
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
        print("VERY NICE")

    return response.json(dict(form=form))
