import datetime
import jwt
from flask import g, current_app
from flask_httpauth import HTTPTokenAuth
from flask_restful import Resource

from api.models import User, BlacklistToken


http_auth = HTTPTokenAuth(scheme='Bearer')


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=600),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return {'id': int(payload['sub'])}
    except jwt.ExpiredSignatureError:
        return {'error': 'Signature expired. Please log in again.'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token. Please log in again.'}


@http_auth.verify_token
def verify_user_token(auth_token):
    blacklist_token = BlacklistToken.query.filter_by(token=auth_token).first()
    if blacklist_token:
        return False
    mess = decode_auth_token(auth_token)
    if 'id' in mess:
        user = User.query.filter_by(id=mess['id']).first()
        if not user:
            return False
        g.user = user
        g.token = str(auth_token)
        return True
    return False


@http_auth.get_user_roles
def get_user_roles(user):
    role = g.user.get_user_role()
    return role


class AuthenticationRequiredResource(Resource):
    method_decorators = [http_auth.login_required(role=['admin', 'user'])]


class AuthenticationAdminRequiredResource(Resource):
    method_decorators = [http_auth.login_required(role='admin')]