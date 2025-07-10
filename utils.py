import jwt
from flask import request

SECRET_KEY = 'junglegym'

def decode_token_from_request():
    token = request.cookies.get('token')
    if not token:
        return None
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
