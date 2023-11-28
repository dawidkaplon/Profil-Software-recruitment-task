import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path


manager_directory = Path(__file__).resolve().parent


class DataHandler:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_database(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT,
                telephone_number TEXT,
                email TEXT,
                password TEXT,
                role TEXT,
                created_at DATETIME,
                children TEXT
            )
        """
        )
        self.add_parsed_data(db_parser.parse_json("users.json"))

    def add_user(self, user_data):
        fixed_phone_num = re.sub(r"\D", "", user_data["telephone_number"])[-9:]
        # phone number with replaced trailing zeros, non-digital chars etc.

        self.cursor.execute(
            """
            INSERT INTO users (firstname, telephone_number, email, password, role, created_at, children)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_data["firstname"],
                fixed_phone_num,
                user_data["email"],
                user_data["password"],
                user_data["role"],
                user_data["created_at"],
                json.dumps(user_data["children"]),
            ),
        )

        self.connection.commit()  # Add record to the database

    def execute_query(self, query):
        self.cursor.execute(query)

    def get_data(self) -> tuple:
        self.execute_query("SELECT created_at FROM users")
        data = self.cursor.fetchall()
        for item in data:
            print(item, "\n\n")

    def add_parsed_data(self, json_data, csv_data=0, xml_data=0):
        for user in json_data:
            if (
                self.validate_email(user["email"]) is True
                and self.validate_phone_num(user["telephone_number"]) is True
            ):
                self.add_user(user)
            else:
                "Incorrect data, skipping.."

    @classmethod
    def validate_email(cls, email) -> bool:
        pattern = re.compile("[A-Za-z\d\.\_\+\-]+@[A-Za-z\d\.\_]+\.[A-Za-z\d]{1,4}")
        # Check if the email meets the criteria in the tasks' Readme file

        if re.match(pattern, email):
            return True
        return False

    @classmethod
    def validate_phone_num(cls, phone_num) -> bool:
        digits = re.sub(r"\D", "", phone_num)[-9:]
        # Check if the number can meet the criteria i.e. no trailing zeros, non-digital chars etc.

        if len(digits) == 9:
            return True
        return False

    def close_connection(self):
        self.connection.close()


class DataParser:
    """Class to parse the data from the given .xml, .csv and .json data files"""

    def __init__(self):
        pass

    def parse_json(self, filename):
        # Absolute path to the data file
        path = manager_directory / "data" / filename

        with open(path, "r") as f:
            json_data = json.load(f)

            return json_data

    def parse_xml(self, filename):
        pass


if __name__ == "__main__":
    db_handler = DataHandler("dbsqlite3")
    db_parser = DataParser()

    db_handler.create_database()

    db_handler.get_data()

    # Close the connection if done
    db_handler.close_connection()
