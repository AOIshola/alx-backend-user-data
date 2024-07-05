#!/usr/bin/env python3
"""Encrypt Password"""

import bcrypt


def hash_password(password: str) -> bytes:
    """Hashes a password and returns bytes"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """Validates that the provided password
    matches the hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
