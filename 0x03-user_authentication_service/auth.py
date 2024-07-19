#!/usr/bin/env python3
""" Auth module
"""

import bcrypt
import uuid
from db import DB
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import User


def _hash_password(password: str) -> bytes:
    """ hash user password
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """ init Database
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ register user and save to database
        """
        try:
            existing_user = self._db.find_user_by(email=email)
            if existing_user:
                raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            new_user = self._db.add_user(email, hashed_password)
            return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """ validate user login details
        """
        try:
            user = self._db.find_user_by(email=email)
            hashed_password = password.encode('utf-8')
            user_password = user.hashed_password
            return bcrypt.checkpw(hashed_password, user_password)
        except (NoResultFound, InvalidRequestError):
            return False

    def _generate_uuid(self):
        """ Generate UUID
        """
        return str(uuid.uuid4())

    def create_session(self, email: str) -> str:
        """ creates a session for a user
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = self._generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        """ get a user from a session id
        """
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except (NoResultFound, InvalidRequestError):
            return None

    def destroy_session(self, user_id: int) -> None:
        """ destroys a user session
        """
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user.id, session_id=None)
        except NoResultFound:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """ generate a token to reset password
        """
        try:
            user = self._db.find_user_by(email=email)
            token = self._generate_uuid()
            self._db.update_user(user, reset_token=token)
            return token
        except ValueError:
            raise ValueError()

    def update_password(self, reset_token: str, password: str) -> None:
        """ updates my password babyyyyyy
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(user.hashed_password)
            self._db.update_user(user, hashed_password=hashed_password,
                                 reset_token=None)
        except (NoResultFound, ValueError):
            raise ValueError()
