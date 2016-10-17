import datetime

#Class Table
db.define_table('userClasses',
                Field('class_name')
                )
#Project Table
db.define_table('project',
                Field('project_name'),
                Field('current_members'),
                Field('project_info'),
                Field('needed_skills'),
                Field('created_on', 'datetime', default=datetime.datetime.utcnow()),
                )
#User Table
db.define_table('student',
                Field('user_email'),
                Field('addtl_info'),
                Field('skills'),
                Field('classes'),
                )

#When submitting a project, the field should not be empty
db.project.project_name.requires = IS_NOT_EMPTY()
db.project.project_info.requires = IS_NOT_EMPTY()