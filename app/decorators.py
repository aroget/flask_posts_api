
from jwt.exceptions import DecodeError, ExpiredSignature

from functools import wraps

from app.models import Token, User
from flask import g, request, jsonify
from app.utils.auth import parse_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        original_token = request.headers.get('Authorization').split()[1]
        token = Token.query.filter_by(token=original_token).first()

        if token is None:
            return jsonify('Token not found'), 401

        g.user_id = payload['sub']

        return f(*args, **kwargs)
    return decorated_function