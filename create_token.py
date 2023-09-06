import jwt
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = os.environ['SECRET_KEY']


def create_token(user):

    payload = {
        "username": user['username']
    }

    token = jwt.encode(payload, SECRET_KEY)

    return token
