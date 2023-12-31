import os
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort, jsonify
)
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from upload_file import allowed_file, s3
from create_token import create_token
from models import (db, connect_db, User, Listing,
                    Message, Image, DEFAULT_PROFILE_IMAGE_URL)
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


BUCKET = os.environ['BUCKET']
UPLOAD_FOLDER = 'user_uploads'

toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# ✔ DONE: User signup/login/logout
# ✔ DONE: /login-authenticate user
# ✔ DONE: /listings: get all listings-GET
# ✔ DONE: /listings : add a new listing-POST
# ✔ DONE: /listings: update a listing-PATCH
# ✔ DONE: /listings: delete a listing-DELETE
# ✔ DONE: /users/user: get user profile-GET
# ✔ DONE: /users/user: edit user profile-POST
# TODO: /users/listings: nice to have
# ✔ DONE: /user/messages: show the messages of a user-GET
# ✔ DONE: /messages: send a message-POST
# ✔ DONE:  /messages: delete a message-POST


@app.post('/signup')
def signup():
    """Handle user signup.
    Create new user, add new user to DB and create a token.
    """

    user_data = request.json
    user = User.signup(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        profile_image_url=DEFAULT_PROFILE_IMAGE_URL,
        bio=user_data['bio'],
        location=user_data['location']
    )

    db.session.commit()
    user = user.to_dict()
    token = create_token(user)

    return {"token": token}


@app.post('/login')
def login():
    """Handle user login and create a token."""

    user = request.json
    print(user)

    username = user['username']
    password = user['password']

    is_login = User.authenticate(username, password)
    if is_login:
        token = create_token(user)
        return {"token": token}

    return "Invalid login credentials"


################################  listing #####################################


@app.get('/listings')
def show_listings():
    """Show all listings."""
    listings = [listing.to_dict() for listing in Listing.query.all()]
    return jsonify(listings=listings)


@app.post('/listings')
def add_new_listing():
    """Add new listing, and return data about the new listing.

    Returns JSON like:
        {listing: [{id, title, username, price, description, is_reserved}]}
    """
    print("we reach add new listing route!!!")

    data = request.json

    listing = Listing(
        title=data['title'],
        username=data['username'],
        price=data['price'],
        description=data['description'],
        is_reserved=False)

    db.session.add(listing)
    db.session.commit()

    # POST requests should return HTTP status of 201 CREATED
    return (jsonify(listing=listing.to_dict()), 201)


@app.get("/listings/<int:listing_id>")
def show_listing(listing_id):
    """Show a single listing by listing_id in request.

    Returns JSON like:
        {listing: {id, title, username, images, price, description, is_reserved}}
    """

    listing = Listing.query.get_or_404(listing_id)
    images = [image.to_dict() for image in listing.images]
    listing = listing.to_dict()
    print("here are the images", images)
    listing['images'] = images
    print("the listing", listing)

    return jsonify(listing=listing)


@app.patch("/listings/<int:listing_id>")
def update_list(listing_id):
    """Update listing from data in request. Return updated listing.

    Returns JSON like:
        {listing: [{id, title, username, price, description, is_reserved}]}
    """

    data = request.json

    listing = Listing.query.get_or_404(listing_id)

    listing.price = data.get('price', listing.price)
    listing.title = data.get('title', listing.title)
    listing.description = data.get('size', listing.description)
    listing.is_reserved = data.get('size', listing.is_reserved)

    db.session.commit()

    return jsonify(listing=listing.to_dict())


@app.delete("/listings/<int:listing_id>")
def delete_listing(listing_id):
    """Delete listing and return confirmation message.

    Returns JSON of {listing: "Deleted"}
    """

    listing = Listing.query.get_or_404(listing_id)

    db.session.delete(listing)
    db.session.commit()

    return jsonify(listing="Deleted")


@app.get('/users/<username>')
def show_user(username):
    """Show user profile."""
    print("username is", username)
    user = User.query.get_or_404(username)
    print("user is", user)
    return jsonify(user=user.to_dict())


@app.post('/users/<username>')
def edit_user(username):
    """Edit user profile."""
    user_data = request.json
    user = User.query.get_or_404(username)

    user.username = user_data['username'] or user.username
    user.email = user_data['email'] or user.email
    user.profile_image_url = user_data['profile_image_url'] or user.profile_image_url
    user.bio = user_data['bio'] or user.bio
    user.location = user_data['location'] or user.location

    db.session.commit()

    return jsonify(user=user.to_dict())


@app.get('/users/<username>/messages')
def show_user_messages(username):
    "Show users' messages."

    user = User.query.get_or_404(username)
    print("this is user => ", user)

    sent_messages = [message.to_dict() for message in user.sent_messages]
    received_messages = [message.to_dict()
                         for message in user.received_messages]
    print("messages", sent_messages)

    return jsonify(messages=[sent_messages, received_messages])


@app.post('/users/<username>/messages')
def send_message(username):
    "Send message to user."

    message_data = request.json
    message = Message(
        text=message_data['text'],
        to_user=message_data['to_user'],
        from_user=message_data['from_user']
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(message=message.to_dict())


@app.delete("/messages/<int:message_id>")
def delete_message(message_id):
    """Delete message and return confirmation message.

    Returns JSON of {message: "Deleted"}
    """

    message = Message.query.get_or_404(message_id)

    db.session.delete(message)
    db.session.commit()

    return jsonify(message="Deleted")


@app.post('/upload')
def upload_file():
    """Receive picture from user upload, save it on local server,
    upload to Amazon S3 and get the image url, then save the image url
     in DB """
    print("we got here!!!!")
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        s3.upload_file(f"{UPLOAD_FOLDER}/{filename}",
                       BUCKET, filename, {'ContentType': 'image/jpeg'})
        image_url = f"https://{BUCKET}.s3.amazonaws.com/{filename}"
        image = Image(
            image_url=image_url,
            listing_id=1
        )
        db.session.add(image)
        db.session.commit()
        return 'file uploaded successfully'

    return 'File uploaded failed'


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404
