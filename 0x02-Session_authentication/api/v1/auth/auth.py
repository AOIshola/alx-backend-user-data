#!/usr/bin/env python3
"""Auth Module"""

from flask import request
from typing import List, TypeVar
import os


class Auth:
    """ Auth class
    """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ defines auth requirement
        """
        if path is None or excluded_paths is None or len(excluded_paths) == 0:
            return True

        # Normalize path
        if path[-1] != '/':
            path += '/'

        for excluded_path in excluded_paths:
            if excluded_path.endswith('*'):
                # excluded_path += '/'
                if path.startswith(excluded_path[:-1]):
                    # print('excluded', excluded_path[:-1])
                    # print('path', path)
                    return False
            elif path == excluded_path:
                return False
        return True

    def authorization_header(self, request=None) -> str:
        """ auth header
        """
        if request is None or request.headers.get('Authorization') is None:
            return None
        return request.headers.get('Authorization')

    def current_user(self, request=None) -> TypeVar('User'):
        """ current authenticated user
        """
        return None

    def session_cookie(self, request=None):
        """ returns a cookie from a request
        """
        if request is None:
            return None
        cookie_name = os.getenv('SESSION_NAME')
        if cookie_name is None:
            return None
        return request.cookies.get(cookie_name)