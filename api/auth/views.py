from flask import request, g
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from api.utils import authentication, pagination, http_status
from api.models import User, BlacklistToken
from api.schemas import UserSchema, LoginSchema, AdminManagementUserSchema
from api.extension import db

admin_management_user_schema = AdminManagementUserSchema()
user_schema = UserSchema()
login_schema = LoginSchema()


class AdminManagementUserResource(authentication.AuthenticationAdminRequiredResource):
    def get(self, id):
        user = User.query.get_or_404(id)
        result = admin_management_user_schema.dump(user)
        return result


class AdminManagementUserListResource(authentication.AuthenticationAdminRequiredResource):
    def get(self):
        pagination_helper = pagination.PaginationHelper(
            request=request,
            query=User.query,
            resource_for_url='auth.userlistresource',
            key_name='results',
            schema=admin_management_user_schema)
        pagination_result = pagination_helper.paginate_query()
        return pagination_result

    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, http_status.HttpStatus.bad_request_400.value
        errors = admin_management_user_schema.validate(user_dict)
        if errors:
            return errors, http_status.HttpStatus.bad_request_400.value
        user_name = user_dict['name']
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user:
            response = {'user':'An user with the name {} already exists'.format(user_name)}
            return response, http_status.HttpStatus.bad_request_400.value
        try:
            user = User(name=user_name, max_todo=user_dict['max_todo'], admin=bool(user_dict['admin']))
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(user_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                dump_result = admin_management_user_schema.dump(query)
                return dump_result, http_status.HttpStatus.created_201.value
            else:
                return {"error": error_message}, http_status.HttpStatus.bad_request_400.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error", str(e)}
            return response, http_status.HttpStatus.bad_request_400.value


class UserResource(authentication.AuthenticationRequiredResource):
    def get(self):
        user = User.query.get_or_404(g.user.id)
        result = user_schema.dump(user)
        return result


class LoginResource(Resource):
    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, http_status.HttpStatus.bad_request_400.value
        errors = login_schema.validate(user_dict)
        if errors:
            return errors, http_status.HttpStatus.bad_request_400.value
        user_name = user_dict['name']
        try:
            existing_user = User.query.filter_by(name=user_name).first()
            if existing_user:
                auth_token = authentication.encode_auth_token(existing_user.id)
                response = {
                    'status':'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token}
                return response, http_status.HttpStatus.ok_200.value
            response = {
                'status': 'error',
                'message': 'User does not exist.'}
            return response, http_status.HttpStatus.not_found_404.value
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            return response, http_status.HttpStatus.internal_server_error_500.value


class RegisterResource(Resource):
    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, http_status.HttpStatus.bad_request_400.value
        user_dict['admin'] = False
        errors = user_schema.validate(user_dict)
        if errors:
            return errors, http_status.HttpStatus.bad_request_400.value
        user_name = user_dict['name']
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user:
            response = {'user':'An user with the name {} already exists'.format(user_name)}
            return response, http_status.HttpStatus.bad_request_400.value
        try:
            user = User(name=user_name, max_todo=user_dict['max_todo'], admin=user_dict['admin'])
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(user_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                auth_token = authentication.encode_auth_token(query.id)
                response = {
                    'status':'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token}
                return response, http_status.HttpStatus.created_201.value
            else:
                return {"error": error_message}, http_status.HttpStatus.bad_request_400.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error", str(e)}
            return response, http_status.HttpStatus.bad_request_400.value


class LogoutResource(authentication.AuthenticationRequiredResource):
    def post(self):
        try:
            blacklist_token = BlacklistToken(token=g.token)
            # insert the token
            blacklist_token.add(blacklist_token)
            response = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            return response, http_status.HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            responseObject = {
                'status': 'error',
                'message': str(e)
            }
            return response, http_status.HttpStatus.bad_request_400.value
