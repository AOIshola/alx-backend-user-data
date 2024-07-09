#!/usr/bin/env python3
"""Basic Auth Module"""

from api.v1.auth.auth import Auth
from base64 import b64decode
from models.user import User
from typing import Tuple, TypeVar


class BasicAuth(Auth):
    """ Basic Auth Class
    """
    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """ Extract base64 auth header
        """
        if authorization_header is None \
                or not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith("Basic "):
            return None
        return authorization_header.split(' ')[1]

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str
                                           ) -> str:
        """ returns the decoded value of a Base64 string
        """
        if base64_authorization_header is None \
                or not isinstance(base64_authorization_header, str):
            return None
        try:
            bytestring = base64_authorization_header.encode()
            text = b64decode(bytestring)
            return text.decode('utf-8')
        except Exception:
            return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str
                                 ) -> Tuple[str, str]:
        """ returns the user email and password
            from the Base64 decoded value
        """
        if decoded_base64_authorization_header is None \
                or not isinstance(decoded_base64_authorization_header, str):
            return (None, None)
        try:
            decoded_base64_authorization_header.index(':')
            email, password = decoded_base64_authorization_header.split(':',
                                                                        1)
            return (email, password)
        except ValueError:
            return (None, None)

    def user_object_from_credentials(self, user_email: str,
                                     user_pwd: str) -> TypeVar('User'):
        """ returns the User instance based on his email and password.
        """
        if user_email is None or not isinstance(user_email, str) \
                or user_pwd is None or not isinstance(user_pwd, str):
            return None
        users = User.search({"email": user_email})
        if not users:
            return None

        user = users[0]
        if not user.is_valid_password(user_pwd):
            return None

        return user

    def current_user(self, request=None) -> TypeVar('User'):
        """ retrieves the User instance for a request
        """
        auth_header = self.authorization_header(request)
        print(auth_header)
        if auth_header is None:
            return None
        base64_auth_header = self.extract_base64_authorization_header(
                auth_header)
        if base64_auth_header is None:
            return None
        base64_auth_header_d = self.decode_base64_authorization_header(
                base64_auth_header)
        if base64_auth_header_d is None:
            return None
        email, password = self.extract_user_credentials(base64_auth_header_d)
        user = self.user_object_from_credentials(email, password)
        return user
