import jwt
import datetime

from app import config

def create_token(user):
    payload = {
        # subject
        'sub': user.id,
        #issued at
        'iat': datetime.datetime.utcnow(),
        #expiry
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }

    token = jwt.encode(payload, config.Config.SECRET_KEY, algorithm='HS256')
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, config.Config.SECRET_KEY, algorithms='HS256')