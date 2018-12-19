# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role of
# `admin` in the access token
from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims, JWTManager

from api import User

jwt = JWTManager()


# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role of
# `admin` in the access token


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        # print(claims)
        if claims['roles'] != 'Admin':
            return jsonify(msg='Admins only!'), 403
        else:
            return fn(*args, **kwargs)

    return wrapper


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.filter_by(username=identity).first()
    # print(user.roles)
    if 'Admin' in user.roles:
        return {'roles': 'Admin'}
    elif 'User' in user.roles:
        return {'roles': 'User'}
    else:
        return {'roles': 'Operate'}
