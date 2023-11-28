import sqlite3
import json
import csv
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

        # Parse the data and populate the database
        self.add_data(db_parser.parse_json("users.json"))

        csv_data1, csv_data2 = db_parser.parse_csv("users_")
        self.add_data(csv_data1)
        self.add_data(csv_data2)

    def add_data(self, user_data):
        for user in user_data:
            fixed_phone_num = re.sub(r"\D", "", user["telephone_number"])[-9:]
            # Phone number with trailing zeros, non-digit characters, etc. replaced.

            if (
                self.validate_email(user["email"]) is True
                and self.validate_phone_num(user["telephone_number"]) is True
                # Verify that all criteria have been successfully met
            ):
                self.cursor.execute(
                    """
                INSERT INTO users (firstname, telephone_number, email, password, role, created_at, children)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user["firstname"],
                        fixed_phone_num,
                        user["email"],
                        user["password"],
                        user["role"],
                        user["created_at"],
                        json.dumps(user["children"]),
                    ),
                )
                self.connection.commit(),  # Add record to the database

            else:
                "Incorrect data, skipping.."

    def get_data(self) -> tuple:
        self.execute_query("SELECT * FROM users")
        data = self.cursor.fetchall()
        for index, item in enumerate(data, start=1):
            print(f"{index}: {item}\n")

    @classmethod
    def validate_email(cls, email) -> bool:
        """Check if the email meets the criteria in the tasks' Readme file"""

        pattern = re.compile("[A-Za-z\d\.\_\+\-]+@[A-Za-z\d\.\_]+\.[A-Za-z\d]{1,4}")

        if re.match(pattern, email):
            return True
        return False

    @classmethod
    def validate_phone_num(cls, phone_num) -> bool:
        """Check if the number can meet the criteria i.e. no trailing zeros, non-digital chars, 9-digits long etc."""

        digits = re.sub(r"\D", "", phone_num)[-9:]

        if len(digits) == 9:
            return True
        return False

    def execute_query(self, query):
        self.cursor.execute(query)

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

    def parse_csv(self, filename):
        path1 = manager_directory / "data" / f"{filename}1.csv"
        path2 = manager_directory / "data" / f"{filename}2.csv"

        csv_data1 = []
        csv_data2 = []

        # Parse 1st csv file
        with open(path1, "r") as csv1:
            reader1 = csv.DictReader(csv1, delimiter=";")
            for row in reader1:
                csv_data1.append(row)

        # Parse 2nd csv file
        with open(path2, "r") as csv2:
            reader2 = csv.DictReader(csv2, delimiter=";")
            for row in reader2:
                csv_data2.append(row)

        return csv_data1, csv_data2


if __name__ == "__main__":
    db_handler = DataHandler("dbsqlite3")
    db_parser = DataParser()

    db_handler.create_database()
    db_handler.get_data()

    # Close the connection if done
    db_handler.close_connection()
