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

listing1 = Listing(
    username="belle",
    photo_url="",
    price=50,
    description="scenic",
    is_reserved=False

)

listing2 = Listing(
    username="dan",
    price=50,
    description="earthy",
    is_reserved=False

)

db.session.add_all([user1, user2, listing1, listing2])
db.session.commit()
