# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

import json

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def index():
    """
    This is the main controller.
    """

    return dict()

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


