# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime

# Courses Table
db.define_table('course',
                Field('course_name'),
                Field('course_id'),
                Field('course_info'),
                # This could be a student object
                Field('enrolled_students'),
                )
# Project Table
db.define_table('project',
                Field('course_id'),
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('project_name'),
                Field('current_members'),
                Field('project_info'),
                Field('needed_skills'),
                Field('created_on', 'datetime', default=datetime.datetime.utcnow()),
                Field('updated_on', 'datetime', update=datetime.datetime.utcnow()),
                )

# Student Table
db.define_table('student',
                Field('user_email'),
                Field('addtl_info'),
                Field('skills'),
                Field('enrolled_courses'),
                )

# When submitting a project, the field should not be empty
db.project.project_name.requires = IS_NOT_EMPTY()
db.project.project_info.requires = IS_NOT_EMPTY()

# Don't display time by default in forms
db.project.created_on.readable = db.project.created_on.writable = False
db.project.updated_on.readable = db.project.updated_on.writable = False
db.project.course_id.readable = db.project.course_id.writable = False

db.course.course_id.readable = db.course.course_id.writable = False
db.course.enrolled_students.readable = db.course.enrolled_students.writable = False

# Don't display user email by default in forms
db.project.user_email.readable = db.project.user_email.writable = False

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
