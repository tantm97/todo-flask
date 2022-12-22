from flask import Blueprint
from flask_restful import Api

from api.auth import views


auth_blueprint = Blueprint('auth', __name__)
auth = Api(auth_blueprint)

auth.add_resource(views.AdminManagementUserListResource,
    '/auth/admin/')
auth.add_resource(views.AdminManagementUserResource,
    '/auth/admin/<int:id>')

auth.add_resource(views.LoginResource,
    '/auth/login/')
auth.add_resource(views.RegisterResource,
    '/auth/register/')
auth.add_resource(views.LogoutResource,
    '/auth/logout/')
auth.add_resource(views.UserResource,
    '/auth/users/')
