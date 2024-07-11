#!/usr/bin/env python3
""" Session Auth View
"""

from api.v1.views import app_views
from api.v1.app import auth
from flask import Blueprint, jsonify, request, abort
from models.user import User
import os


session_auth = Blueprint('session_auth', __name__)


@session_auth.route('/auth_session/login', methods=['POST'],
                    strict_slashes=False)
def login():
    """ Handle user login
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if email is None or email == "":
        return jsonify({"error": "email missing"}), 400

    if password is None or password == "":
        return jsonify({"error": "password missing"}), 400

    users = User.search({"email": email})
    if not users:
        return jsonify({"error": "no user found for this email"}), 404

    user = users[0]
    if not user.is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401

    session_id = auth.create_session(user.id)
    response = jsonify(user.to_json())
    cookie_name = os.getenv('SESSION_NAME')
    response.set_cookie(cookie_name, session_id)

    return response


@session_auth.route('/auth_session/logout', methods=['DELETE'],
                    strict_slashes=False)
def logout():
    """ Handle user logout
    """
    if not auth.destroy_session(request):
        abort(404)

    return jsonify({}), 200
