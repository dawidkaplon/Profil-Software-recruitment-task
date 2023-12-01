import pytest
import sqlite3
from pathlib import Path

import script
from database import db_manager, db_parser

TEST_DATA = db_parser.DataParser.parse_json("users.json")

@pytest.fixture
def temporary_db():
    """Create a temporary database for testing purposes"""

    connection = sqlite3.connect("temp_db")
    cursor = connection.cursor()

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS users (
                telephone_number TEXT,
                email TEXT
            )
        """
    )

    yield connection, cursor

    connection.close()
    file_path = Path("temp_db")
    file_path.unlink()

def clear_test_database(cursor):
    """After each test, delete all records from the database"""

    cursor.execute(
        """
        DELETE FROM users
        """
    )


class TestDataValidator:
    def test_email(self, temporary_db):
        """Check if e-mail that meets criteria has been successfully added into the database"""

        connection, cursor = temporary_db  # Unpack as the temporary_db fixture is a tuple
        correct_emails = 0
        incorrect_emails = 0

        for user in TEST_DATA:
            if db_manager.DataHandler.validate_email(user["email"]):
                cursor.execute(
                    """
                    INSERT INTO users (email)
                    VALUES (?)
                    """,
                    (user["email"],),
                )
                correct_emails += 1
            else:
                incorrect_emails += 1

        cursor.execute(
            """
            SELECT COUNT(1) FROM users
            """
        )
        result = cursor.fetchone()[0]

        assert (
            result == correct_emails
        )  #  Number of rows in db should equal to correct emails
        
        assert (
            ((len(TEST_DATA)) - result) == incorrect_emails
        )  # Number of rows not added to db should be the same as incorrect emails

        clear_test_database(cursor)

    def test_phone_number(self, temporary_db):
        """Check if correct phone-num has been added into the database"""

        connection, cursor = temporary_db
        correct_phone_numbers = 0
        incorrect_phone_numbers = 0

        for user in TEST_DATA:
            if db_manager.DataHandler.validate_phone_num(user["telephone_number"]):
                cursor.execute(
                    """
                    INSERT INTO users (telephone_number)
                    VALUES (?)
                    """,
                    (user["telephone_number"],),
                )
                correct_phone_numbers += 1
            else:
                incorrect_phone_numbers += 1

        cursor.execute(
            """
            SELECT COUNT(1) FROM users
            """
        )

        result = cursor.fetchone()[0]

        assert (
            result == correct_phone_numbers  
            # Return True if the number of rows in the db is the same as the number of valid phone numbers in the dataset
        )
        assert (
            ((len(TEST_DATA)) - result) == incorrect_phone_numbers
        )
