import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort, jsonify
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import jwt

from models import (db, connect_db, User, Listing,
                    Message, DEFAULT_PROFILE_IMAGE_URL)
from create_token import create_token

CURR_USER_KEY = "curr_user"

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
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
# TODO: /users/listings: nice to have
# TODO: /upload: upload pic-POST
# TODO: /user/messages: show the messages of a user-GET
# TODO: /messages: send a message-POST
# TODO: /messages: delete a message-POST


@app.post('/signup')
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
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
    """Handle user login and redirect to homepage on success."""

    user = request.json
    print(user)

    username = user['username']
    password = user['password']

    is_login = User.authenticate(username, password)
    if is_login:
        token = create_token(user)
        return {"token": token}

    return "Invalid login credentials"

# TODO: React will take care of logout


@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")

################################  listing #####################################


@app.get('/listings')
def show_listings():
    listings = [listing.to_dict() for listing in Listing.query.all()]
    return jsonify(listings=listings)

@app.post('/listings')
def add_new_listing():
    """Add new listing, and return data about the new listing.

    Returns JSON like:
        {cupcake: [{id, username, photo_url, price, description, is_reserved}]}
    """

    data = request.json

    listing = Listing(
    username=data['username'],
    photo_url=data['photo_url'] or None,
    price=data['price'],
    description=data['description'],
    is_reserved=False)

    db.session.add(listing)
    db.session.commit()

    # POST requests should return HTTP status of 201 CREATED
    return (jsonify(listing=listing.to_dict()), 201)

@app.patch("/listings/<int:listing_id>")
def update_list(listing_id):
    """Update listing from data in request. Return updated listing.

    Returns JSON like:
        {cupcake: [{id, username, photo_url, price, description, is_reserved}]}
    """

    data = request.json

    listing = Listing.query.get_or_404(listing_id)

    listing.photo_url = data.get('flavor', listing.photo_url)
    listing.price = data.get('price', listing.price)
    listing.description = data.get('size', listing.description)
    listing.is_reserved = data.get('size', listing.is_reserved)


    db.session.add(listing)
    db.session.commit()

    return jsonify(listing=listing.to_dict())

@app.delete("/listings/<int:listing_id>")
def delete_listing(listing_id):
    """Delete listing and return confirmation message.

    Returns JSON of {message: "Deleted"}
    """

    listing = Listing.query.get_or_404(listing_id)

    db.session.delete(listing)
    db.session.commit()

    return jsonify(deleted=listing_id)





@app.get('/users/<username>')
def show_user(username):
    """Show user profile."""
    print("username is", username)
    user = User.query.get_or_404(username)
    print("user is", user)
    return jsonify(user=user.to_dict())




# TODO: route for patch user


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user.

    Redirect to user page on success.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
            user.header_image_url = (
                form.header_image_url.data or DEFAULT_HEADER_IMAGE_URL)
            user.bio = form.bio.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

# TODO: route for delete user


@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    Message.query.filter_by(user_id=g.user.id).delete()
    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404
