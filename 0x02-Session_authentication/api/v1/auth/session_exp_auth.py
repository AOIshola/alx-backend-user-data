#!/usr/bin/env python3
""" Session Expiration Auth
"""

from api.v1.auth.session_auth import SessionAuth
from datetime import datetime, timedelta
import os


class SessionExpAuth(SessionAuth):
    """ Session Expiration Auth Class
    """
    def __init__(self):
        """ Initialize the SessionExpAuth class
        """
        super().__init__()
        try:
            self.session_duration = int(os.getenv('SESSION_DURATION', 0))
        except ValueError:
            self.session_duration = 0

    def create_session(self, user_id=None):
        """ Create a session with expiration
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None

        session_info = {
            "user_id": user_id,
            "created_at": datetime.now()
        }

        self.user_id_by_session_id[session_id] = session_info
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """ Get user_id from session_id with expiration check
        """
        if session_id is None:
            return None

        session_info = self.user_id_by_session_id.get(session_id)
        if session_info is None:
            return None

        if self.session_duration <= 0:
            return session_info.get("user_id")

        created_at = session_info.get("created_at")
        if created_at is None:
            return None

        if created_at + timedelta(seconds=self.session_duration) \
                < datetime.now():
            return None

        return session_info.get("user_id")
