import secrets
import datetime
from functools import wraps

import jwt
from flask import request
from flask_restplus import reqparse

class AuthToken:
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(16)

    def generate(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        return jwt.encode(payload, key=self.secret_key, algorithm='HS256')

    def validate(self, token):
        try:
            return jwt.decode(token.encode(), key=self.secret_key, algorithm='HS256')
        except:
            raise

def authenticate(api, auth):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = request.headers.get('AUTH_TOKEN')
            if token:
                try:
                    auth.validate(token)
                    return f(*args, **kwargs)
                except jwt.ExpiredSignatureError:
                    api.abort(401, "Token expired")
                except jwt.InvalidSignatureError:
                    api.abort(401, "Token signature mismatch")
                except:
                    api.abort(500)
            else:
                api.abort(401, 'Token missing')

        return inner
    return decorator
