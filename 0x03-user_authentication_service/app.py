#!/usr/bin/env python3
""" App Module
"""

from auth import Auth
from flask import Flask, jsonify, request, abort, redirect, url_for


app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET', ])
def index():
    """ simple index GET route
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users():
    """ register users
    """
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": f"{email}", "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    """ login user and create a session for user
        with session_id stored as a cookie
    """
    email = request.form.get('email')
    password = request.form.get('password')
    is_valid = AUTH.valid_login(email, password)
    if not is_valid:
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({'email': email, 'message': "logged in"})
    response.set_cookie('session_id', session_id)

    return response


@app.route('/logout', methods=['DELETE'], strict_slashes=False)
def logout():
    """ logs a user out and destroys the session
    """
    session_id = request.cookies.get('session_id')
    user = AUTH._db.find_user_by(session_id=session_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect(url_for("index"))


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    """ user profile
    """
    session_id = request.cookies.get('session_id')
    user = AUTH._db.find_user_by(session_id=session_id)
    if not user:
        abort(403)
    return jsonify({"email": user.email}), 200


@app.route('/reset_password', methods=['POST', 'PUT'], strict_slashes=False)
def get_reset_password_token():
    """ get reset password token
    """
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token})
    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """ Update password
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"})
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
