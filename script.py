import argparse
import re
import json
from sqlite3 import OperationalError
from collections import Counter

from database.db_manager import DataHandler


def authenticate(func):
    """
    Decorator checking whether the database has been built
    and whether the correct access data has been provided
    """

    def wrapper(self, login, password):
        try:
            if db_handler.validate_email(login):  # Case where e-mail as Login was given
                db_handler.cursor.execute(
                    """
                    SELECT password
                    FROM users
                    WHERE email=?
                    """,
                    (login,),
                )
                result = db_handler.cursor.fetchone()[0]

                if password == result:
                    func(
                        self, login, password
                    )  #  Authentication succeeded, task will be executed
                else:
                    print("Invalid Login")

            elif db_handler.validate_phone_num(
                login
            ):  # Phone-number as Login was given
                login = re.sub(r"\D", "", login)[-9:]

                db_handler.cursor.execute(
                    """
                    SELECT password
                    FROM users
                    WHERE telephone_number=?
                    """,
                    (login,),
                )
                result = db_handler.cursor.fetchone()[0]
                if password == result:
                    func(self, login, password)
                else:
                    print("Invalid Login")

            else:
                print("Invalid Login")

        except TypeError:
            print("Invalid Login")

        except OperationalError:
            print(
                "Database is not created yet! Type 'python script.py create_database' to build one"
            )

    return wrapper


def check_if_admin(login):
    """Simple function to check if the given user has an admin role"""
    if "@" in login:
        db_handler.cursor.execute(
            """
            SELECT role 
            FROM users
            WHERE email=?
            """,
            (login,),
        )
    else:
        db_handler.cursor.execute(
            """
            SELECT role 
            FROM users
            WHERE telephone_number=?
            """,
            (login,),
        )

    result = db_handler.cursor.fetchone()[0]

    if result == "admin":
        return True
    else:
        return False


class Scripts:
    def __init__(self):
        pass

    def create_database(self):
        db_handler.create_database()
        print("Database has been successfully created and populated")

    """ADMIN ONLY METHODS"""

    @authenticate
    def print_all_accounts(self, login, password):
        """Return the total number (int) of valid accounts"""

        if check_if_admin(login):
            db_handler.cursor.execute(
                """
                SELECT COUNT(1) FROM users
                """
            )
            result = db_handler.cursor.fetchone()[0]
            print(int(result))
        else:
            print("Invalid Login")

    @authenticate
    def print_oldest_account(self, login, password):
        if check_if_admin(login):
            db_handler.cursor.execute(
                """
                SELECT *
                FROM users
                ORDER BY created_at ASC
                """
            )
            result = db_handler.cursor.fetchone()
            print(
                f"name: {result[1]}\nemail_address: {result[3]}\ncreated_at: {result[6]}"
            )

        else:
            print("Invalid Login")

    @authenticate
    def group_by_age(self, login, password):
        """Group children by age, sort by count (ascending)"""
        if check_if_admin(login):
            children_age = []

            db_handler.cursor.execute(
                """
                SELECT children
                FROM users
                """
            )
            result = db_handler.cursor.fetchall()

            for row in result:
                for age in re.findall(r"\d+", row[0]):
                    children_age.append(int(age))
            print(children_age)
            c = Counter(children_age)
            sorted_age = dict(sorted(c.items(), key=lambda x: x[1]))
            for key, value in sorted_age.items():
                print(f"age: {key}, count: {value}")

        else:
            print("Invalid Login")

    """BOTH ADMIN AND USER METHODS"""

    @authenticate
    def print_children(self, login, password):
        """Return personal data of the logged-in user's children, sorted by name"""

        if "@" in login:
            db_handler.cursor.execute(
                """
                    SELECT children
                    FROM users
                    WHERE email=?   
                """,
                (login,),
            )
        else:
            db_handler.cursor.execute(
                """
            SELECT children
            FROM users
            WHERE telephone_number=?
            """,
                (login,),
            )

        # Fetch the result
        result = db_handler.cursor.fetchone()

        if result[0] != "[]":
            children_data = json.loads(result[0])  # Extract the children data

            sorted_children = sorted(children_data, key=lambda x: x.get("name", ""))

            for child in sorted_children:
                print(f"{child['name']}, {child['age']}")
        else:
            print("This user has no children")

    @authenticate
    def find_similar_children_by_age(self, login, password):
        """Find users with children of the same age as at least user's one own child"""

        user_children_age = []
        common_users = []  # Avoid duplicating the output list of rows
        common_phone_numbers = []  # --||--

        if "@" in login:
            db_handler.cursor.execute(
                """
                SELECT children
                FROM users
                WHERE email=?
                """,
                (login,),
            )
        else:
            db_handler.cursor.execute(
                """
                SELECT children
                FROM users
                WHERE telephone_number=?
                """,
                (login,),
            )

        result = json.loads(db_handler.cursor.fetchone()[0])
        for child in result:
            user_children_age.append(child["age"])  # Get the age of user's each child

        db_handler.cursor.execute(
            """
            SELECT firstname, telephone_number, children
            FROM users
            """
        )
        result = db_handler.cursor.fetchall()

        for user in result:
            children_data = json.loads(user[2])
            user_phone_number = user[1]

            for child in children_data:
                if child["age"] in user_children_age:
                    if user_phone_number not in common_phone_numbers:
                        common_users.append(
                            {
                                "firstname": user[0],
                                "phone_number": user_phone_number,
                                "children": children_data,
                            }
                        )
                        common_phone_numbers.append(user_phone_number)
        for user in common_users:
            children = sorted(
                user["children"], key=lambda x: x.get("name", "")
            )  # Sort children alphabetically by names
            response = f'{user["firstname"]}, {user["phone_number"]}: '

            for child in children:
                response += f'{child["name"]}, {child["age"]}; '

            print(response[:-2])


if __name__ == "__main__":
    db_handler = DataHandler("dbsqlite3")
    parser = argparse.ArgumentParser()
    scripts = Scripts()

    parser.add_argument(
        "action",
        choices=[
            "create_database",
            "print-all-accounts",
            "print-oldest-account",
            "group-by-age",
            "print-children",
            "find-similar-children-by-age",
        ],
    )
    parser.add_argument("--login", help="Login information", const=0, nargs="?")
    parser.add_argument("--password", help="Password information", const=0, nargs="?")

    args = parser.parse_args()

    if (
        args.action == "create_database"
    ):  # if ' bash: syntax error near unexpected token `(' ' :
        # most likely put everything in parenthesses
        scripts.create_database()

    elif args.action == "print-all-accounts":
        scripts.print_all_accounts(args.login, args.password)

    elif args.action == "print-oldest-account":
        scripts.print_oldest_account(args.login, args.password)

    elif args.action == "group-by-age":
        scripts.group_by_age(args.login, args.password)

    elif args.action == "print-children":
        scripts.print_children(args.login, args.password)

    elif args.action == "find-similar-children-by-age":
        scripts.find_similar_children_by_age(args.login, args.password)
