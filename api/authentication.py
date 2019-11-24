import secrets
import datetime
from functools import wraps

import jwt
from flask import request

class AuthToken:
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(16)

    def generate(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        return jwt.encode(payload, key=self.secret_key, algorithms=['HS256'])

    def validate(self, token):
        try {
            return jwt.decode(token, key=self.secret_key, algorithms=['HS256'])
        }
        except jwt.ExpiredSignatureError:
            raise

def authenticate(auth, f):
    @wraps(f)
    def inner(*args, **kwargs):
        token = request.headers.get('AUTH_TOKEN')
        if token:
            try:
                auth.validate(token)
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                abort(401, "Token expired")
            except:
                abort(500)
        else:
            abort(401, 'Token missing')

    return inner
