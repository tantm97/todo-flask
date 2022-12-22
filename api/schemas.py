from marshmallow import fields, validate, EXCLUDE

from api.extension import ma


class AdminManagementUserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
        validate=validate.Length(3))
    max_todo = fields.Integer(required=True, 
        validate=validate.Range(min=1, error="Value must be greater than 0"))
    url = ma.URLFor('auth.adminmanagementuserresource',
        id='<id>',
        _external=True)
    admin = fields.Boolean(required=True)
    tasks = fields.Nested('TaskSchema',
        many=True,
        exclude=('user',))

    class Meta:
        unknown = EXCLUDE


class AdminManagementTaskSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    message = fields.String(required=True,
        validate=validate.Length(5))
    creation_date = fields.DateTime()
    user = fields.Nested(AdminManagementUserSchema,
        only=['id', 'url', 'name', 'max_todo'])
    url = ma.URLFor('task.taskresource', 
        id='<id>', 
        _external=True)


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
        validate=validate.Length(3))
    max_todo = fields.Integer(required=True, 
        validate=validate.Range(min=1, error="Value must be greater than 0"))
    admin = fields.Boolean(required=True)
    tasks = fields.Nested('TaskSchema',
        many=True,
        exclude=('user',))

    class Meta:
        unknown = EXCLUDE


class TaskSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    message = fields.String(required=True,
        validate=validate.Length(5))
    creation_date = fields.DateTime()
    user = fields.Nested(UserSchema,
        only=['id', 'name', 'max_todo', 'admin'])
    url = ma.URLFor('task.taskresource', 
        id='<id>', 
        _external=True)


class LoginSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
        validate=validate.Length(3))
    password = fields.String(required=True)
    