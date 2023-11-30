import argparse
import re
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
        if check_if_admin(login):
            db_handler.cursor.execute(
                """
                SELECT COUNT(1) FROM users
                """
            )
            result = db_handler.cursor.fetchone()[0]
            print(int(result))

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

            c = Counter(children_age)
            sorted_age = dict(sorted(c.items(), key=lambda x: x[1]))

            for key, value in sorted_age.items():
                print(f"age: {key}, count: {value}")

        else:
            print("Invalid Login")

    """BOTH ADMIN AND USER METHODS"""


if __name__ == "__main__":
    db_handler = DataHandler("dbsqlite3")
    parser = argparse.ArgumentParser()
    scripts = Scripts()

    parser.add_argument(
        "action",
        choices=[
            "create_database",
            "test",
            "print-all-accounts",
            "print-oldest-account",
            "group-by-age",
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
