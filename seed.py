"""Seed database with sample data."""

from app import db
from models import User, Listing, Message

db.drop_all()
db.create_all()

user1 = User(
    username="belle",
    email="belle@belle.com",
    password="password",
    profile_image_url="",
    bio="test only",
    location="NY"

)

user2 = User(
    username="dan",
    email="dan@dan.com",
    password="password",
    profile_image_url="",
    bio="test only",
    location="NYC"

)

db.session.add_all([user1, user2])
db.session.commit()



