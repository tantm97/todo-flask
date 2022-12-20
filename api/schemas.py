from marshmallow import fields, validate, EXCLUDE

from api.extension import ma


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
        validate=validate.Length(3))
    max_todo = fields.Integer(strict=True, require=True, 
        validate=[validate.Range(min=1, error="Value must be greater than 0")])
    url = ma.URLFor('auth.userresource',
        id='<id>',
        _external=True)
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
        only=['id', 'url', 'name', 'max_todo'],
        require=True)
    url = ma.URLFor('task.taskresource', 
        id='<id>', 
        _external=True)
