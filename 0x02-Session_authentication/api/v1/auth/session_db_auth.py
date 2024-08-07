#!/usr/bin/env python3
""" SessionDBAuth module
"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession
from datetime import datetime, timedelta


class SessionDBAuth(SessionExpAuth):
    """ Session DB Auth Class
    """
    def create_session(self, user_id=None):
        """ Create a session and store it in the database
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        
        session_info = {
            'user_id': user_id,
            'session_id': session_id
        }

        user_session = UserSession(**session_info)
        user_session.save()

        return session_id

    def user_id_for_session_id(self, session_id=None):
        """ Get user_id from session_id by querying the database
        """
        if session_id is None:
            return None

        user_sessions = UserSession.search({'session_id': session_id})
        if not user_sessions:
            return None
        
        user_session = user_sessions[0]
        if self.session_duration <= 0:
            return user_session.user_id

        created_at = user_session.created_at
        if created_at is None:
            return None

        if created_at + timedelta(seconds=self.session_duration) < datetime.now():
            return None

        return user_session.user_id

    def destroy_session(self, request=None):
        """ Destroy the session from the database
        """
        if request is None:
            return False

        session_id = self.session_cookie(request)
        if session_id is None:
            return False

        user_sessions = UserSession.search({'session_id': session_id})
        if not user_sessions:
            return False

        user_session = user_sessions[0]
        user_session.remove()
        return True
