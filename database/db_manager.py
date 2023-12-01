import sqlite3
import json
import re
from datetime import datetime

from .db_parser import DataParser


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
        self.add_data(DataParser.parse_json("users.json"))

        csv_data1, csv_data2 = DataParser.parse_csv("users_")
        self.add_data(csv_data1)
        self.add_data(csv_data2)

        xml_data1, xml_data2 = DataParser.parse_xml("users_")
        self.add_data(xml_data1)
        self.add_data(xml_data2)

    def add_data(self, user_data):
        """Verify the provided data and then, add it to the database"""
        for user in user_data:
            current_system_time = datetime.now()
            current_user_time = datetime.strptime(
                user["created_at"], "%Y-%m-%d %H:%M:%S"
            )

            # Phone number with trailing zeros, non-digit characters, etc. replaced.
            fixed_phone_num = re.sub(r"\D", "", user["telephone_number"])[-9:]

            if (
                # Verify that all criteria have been successfully met
                self.validate_email(user["email"]) is True
                and self.validate_phone_num(user["telephone_number"]) is True
            ):
                data_repeated = self.check_if_data_is_repeated(user, fixed_phone_num)
                if not data_repeated:  # Add the data if no repetitions were found
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
                    (self.connection.commit(),)

                elif data_repeated == "email_repeated":
                    self.cursor.execute(
                        """
                        SELECT created_at
                        FROM users
                        WHERE email=?
                        """,
                        (user["email"],),
                    )
                    database_record_time = datetime.strptime(
                        self.cursor.fetchone()[0], "%Y-%m-%d %H:%M:%S"
                    )

                    database_record_time_difference = (
                        current_system_time - database_record_time
                    )
                    current_user_time_difference = (
                        current_system_time - current_user_time
                    )

                    if database_record_time_difference < current_user_time_difference:
                        pass
                    else:  # Newer record was found: replace the old one
                        self.cursor.execute(
                            """
                            UPDATE users
                            SET firstname=?, telephone_number=?, email=?, password=?, role=?, created_at=?, children=?
                            WHERE email=?
                            """,
                            (
                                user["firstname"],
                                fixed_phone_num,
                                user["email"],
                                user["password"],
                                user["role"],
                                user["created_at"],
                                json.dumps(user["children"]),
                                user["email"],
                            ),
                        )
                    (self.connection.commit(),)

                elif data_repeated == "number_repeated":
                    self.cursor.execute(
                        """
                            UPDATE users
                            SET firstname=?, telephone_number=?, email=?, password=?, role=?, created_at=?, children=?
                            WHERE telephone_number=?
                            """,
                        (
                            user["firstname"],
                            fixed_phone_num,
                            user["email"],
                            user["password"],
                            user["role"],
                            user["created_at"],
                            json.dumps(user["children"]),
                            fixed_phone_num,
                        ),
                    )
                    (self.connection.commit(),)
            else:
                pass

    @classmethod
    def validate_email(cls, email) -> bool:
        """Check if the email meets the criteria in the tasks' Readme file"""

        pattern = re.compile("^[A-Za-z\d\.\_\+\-]+@[A-Za-z\d\.\_]+\.[A-Za-z\d]{1,4}$")

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

    def check_if_data_is_repeated(self, user_data, phone_num):
        """Check if the e-mail address or phone number was repeated when adding data to the database"""

        self.cursor.execute(
            """SELECT email
                        FROM users
                        WHERE email=?
                        """,
            (user_data["email"],),
        )

        result = self.cursor.fetchone()

        if result:
            return "email_repeated"
        else:
            self.cursor.execute(
                """SELECT telephone_number
                        FROM users
                        WHERE telephone_number=?
                        """,
                (phone_num,),
            )
            result = self.cursor.fetchone()

            if result:
                return "number_repeated"
            else:
                return False
