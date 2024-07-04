#!/usr/bin/env python3
"""Logging PII data"""

import logging
import re
import os
import mysql.connector
from mysql.connector import connection
from typing import List,  Tuple


# Define the PII_FIELDS tuple with the fields considered as PII
PII_FIELDS: Tuple[str, ...] = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str],
                 redaction: str, message: str, separator: str) -> str:
    """Returns log message obfuscated"""
    pattern = "|".join(fr'(?<={field}=)[^{separator}]*' for field in fields)
    return re.sub(pattern, redaction, message)


def get_db() -> connection.MySQLConnection:
    """Connect to the MySQL database and return the connection object."""
    username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    return mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=db_name
    )


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        message = super(RedactingFormatter, self).format(record)
        return filter_datum(self.fields, self.REDACTION, message,
                            self.SEPARATOR)


def get_logger() -> logging.Logger:
    """Creates and returns a logger object."""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()

    formatter = RedactingFormatter(fields=list(PII_FIELDS))
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


def main():
    """Main function to connect to the database and log user data."""
    logger = get_logger()
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM users"
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]

    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))
        log_message = "; ".join(f"{key}={value}" for key,
                                value in row_dict.items())
        logger.info(log_message)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()