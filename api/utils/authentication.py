from flask import g
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.models import User


http_auth = HTTPBasicAuth()


@http_auth.verify_password
def verify_user_passowrd(name, password):
    user = User.query.filter_by(name=name).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class AuthenticationRequiredResource(Resource):
    method_decorators = [http_auth.login_required]