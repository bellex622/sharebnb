import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort,
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import jwt

SECRET_KEY = os.environ['SECRET_KEY']


def create_token(user):

    payload = {
    "username": user['username']
    }


    token = jwt.encode(payload,SECRET_KEY)

    return token
