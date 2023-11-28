import sqlite3
import json
import csv
import re
import xml.etree.ElementTree as ET
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

        xml_data1, xml_data2 = db_parser.parse_xml("users_")
        self.add_data(xml_data1)
        self.add_data(xml_data2)

    def add_data(self, user_data):
        """Verify the provided data and then, add it to the database"""
        for user in user_data:
            fixed_phone_num = re.sub(r"\D", "", user["telephone_number"])[-9:]
            # Phone number with trailing zeros, non-digit characters, etc. replaced.

            if (
                self.validate_email(user["email"]) is True
                and self.validate_phone_num(user["telephone_number"]) is True
                # Verify that all criteria have been successfully met
            ):
                data_repeated = self.check_if_data_is_repeated(user, fixed_phone_num)
                if not data_repeated:  # Add data if no repetitions were found
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
                    self.connection.commit(),

                elif data_repeated == 'email_repeated':
                    """TO DO: CHECK WHICH ENTRY WAS NEWER BASED ON THE TIMESTAMP"""
                    pass
                
                elif data_repeated == 'number_repeated':
                    """TO DO: CHECK WHICH ENTRY WAS NEWER BASED ON THE TIMESTAMP"""
                    pass
                    
            else:
                pass

    def get_data(self) -> tuple:
        self.execute_query("SELECT * FROM users")
        data = self.cursor.fetchall()
        for record in data:
            print(record[0], ": ", record[1], ", ", record[3], ", ", record[2])

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

    def check_if_data_is_repeated(self, user_data, phone_num) -> bool:
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
        path1 = manager_directory / "data" / f"{filename}1.xml"
        path2 = manager_directory / "data" / f"{filename}2.xml"

        xml_data1 = []
        xml_data2 = []

        tree1 = ET.parse(path1)
        root1 = tree1.getroot()

        tree2 = ET.parse(path2)
        root2 = tree2.getroot()

        roots_to_use = [root1, root2]
        data_containers = [xml_data1, xml_data2]

        for i in range(2):  # DRY :)
            for user in roots_to_use[i].findall("user"):
                user_data = {}
                user_data["firstname"] = user.find("firstname").text
                user_data["telephone_number"] = user.find("telephone_number").text
                user_data["email"] = user.find("email").text
                user_data["password"] = user.find("password").text
                user_data["role"] = user.find("role").text
                user_data["created_at"] = user.find("created_at").text

                if (
                    user.findall(".//child") == []
                ):  # Set children list to empty when no record was found
                    user_data["children"] = []
                else:
                    for child in user.findall(".//child"):
                        child_data = {}
                        child_data["name"] = child.findtext("name")
                        child_data["age"] = child.findtext("age")
                        user_data["children"] = user_data.get("children", []) + [
                            child_data
                        ]
                data_containers[i].append(user_data)

        return xml_data1, xml_data2

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
