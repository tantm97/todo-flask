from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from api.utils import authentication, pagination, http_status
from api.models import User
from api.schemas import UserSchema
from api.extension import db


user_schema = UserSchema()


class UserResource(authentication.AuthenticationRequiredResource):
    def get(self, id):
        user = User.query.get_or_404(id)
        result = user_schema.dump(user)
        return result


class UserListResource(Resource):
    @authentication.http_auth.login_required
    def get(self):
        pagination_helper = pagination.PaginationHelper(
            request=request,
            query=User.query,
            resource_for_url='auth.userlistresource',
            key_name='results',
            schema=user_schema)
        pagination_result = pagination_helper.paginate_query()
        return pagination_result

    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, http_status.HttpStatus.bad_request_400.value
        errors = user_schema.validate(user_dict)
        if errors:
            return errors, http_status.HttpStatus.bad_request_400.value
        user_name = user_dict['name']
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user:
            response = {'user':'An user with the name {} already exists'.format(user_name)}
            return response, http_status.HttpStatus.bad_request_400
        try:
            user = User(name=user_name)
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(user_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                dump_result = user_schema.dump(query)
                return dump_result, http_status.HttpStatus.created_201.value
            else:
                return {"error": error_message}, http_status.HttpStatus.bad_request_400
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error", str(e)}
            return response, http_status.HttpStatus.bad_request_400.value

