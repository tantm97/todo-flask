from flask import Blueprint
from flask_restful import Api

from api.auth import views


auth_blueprint = Blueprint('auth', __name__)
auth = Api(auth_blueprint)

auth.add_resource(views.UserListResource,
    '/auth/users/')
auth.add_resource(views.UserResource,
    '/auth/users/<int:id>')
