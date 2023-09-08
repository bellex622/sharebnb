"""SQLAlchemy models for ShareBNB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_PROFILE_IMAGE_URL = "https://fdsfsd.com/d.jpg"
DEFAULT_PHOTO_URL = "https://fdsfsd.com/d.jpg"


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)


class Image(db.Model):
    """Image URL from S3 bucket."""

    __tablename__ = 'images'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id'),
    )

    def to_dict(self):
        """Serialize user info to a dict."""

        return {
        "id": self.id,
        "image_url": self.image_url
        }


class Message(db.Model):
    """Messages between hosts and guests."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.Text,
        nullable=False,
    )

    sent_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    read_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    from_user = db.Column(
        db.String(30),
        db.ForeignKey('users.username'),
        nullable=False,
    )

    to_user = db.Column(
        db.String(30),
        db.ForeignKey('users.username'),
        nullable=False,
    )

    def to_dict(self):
        """Serialize user info to a dict."""

        return {
            "text": self.text,
            "sent_at": self.sent_at,
            "read_at": self.read_at,
            "from_user": self.from_user,
            "to_user": self.to_user,
        }


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
        primary_key=True,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    profile_image_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_PROFILE_IMAGE_URL,
    )

    bio = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    location = db.Column(
        db.String(30),
        nullable=False,
        default="",
    )

    password = db.Column(
        db.String(100),
        nullable=False,
    )

    listings = db.relationship('Listing', backref="user")
    # sent_to_user = db.relationship(
    #     "User",
    #     secondary="messages",
    #     primaryjoin=(Message.to_user==id),
    #     secondaryjoin=(Message.from_user==id),
    #     backref="received_from_user",
    # )
    # backref: message.sender
    sent_messages = db.relationship(
        "Message", backref="sender", foreign_keys="Message.from_user")
    received_messages = db.relationship(
        "Message", backref="receiver", foreign_keys="Message.to_user")

    def __repr__(self):
        return f"<User #{self.username}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, profile_image_url=DEFAULT_PROFILE_IMAGE_URL, bio="", location=""):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            profile_image_url=profile_image_url,
            bio=bio,
            location=location
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def to_dict(self):
        """Serialize user info to a dict."""

        return {
            "username": self.username,
            "email": self.email,
            "profile_image_url": self.profile_image_url,
            "bio": self.bio,
            "location": self.location,
        }


class Listing(db.Model):
    """Outdoor space listings."""

    __tablename__ = 'listings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(30),
        db.ForeignKey('users.username')
    )

    price = db.Column(
        db.Integer,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    is_reserved = db.Column(
        db.Boolean,
        default=False
    )

    images = db.relationship("Image", backref="listing")

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "username": self.username,
            "price": self.price,
            "description": self.description,
            "is_reserved": self.is_reserved,
        }
