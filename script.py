import argparse
import re
from sqlite3 import OperationalError

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

            elif db_handler.validate_phone_num(login):  # Phone-number as Login was given
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
                'Database is not created yet! Type "python3 script.py create_database" to build one'
            )

    return wrapper


class Scripts:
    def __init__(self):
        pass

    def create_database(self):
        db_handler.create_database()
        print("Database has been successfully created and populated")

    @authenticate
    def test(self, login, password):
        print(f"Login: {login}, password: {password}")


if __name__ == "__main__":
    db_handler = DataHandler("dbsqlite3")
    parser = argparse.ArgumentParser()
    scripts = Scripts()

    parser.add_argument("action", choices=["create_database", "test"])
    parser.add_argument("--login", help='Login information')
    parser.add_argument("--password", help='Password information')


    args = parser.parse_args()
    if args.action == "create_database":
        scripts.create_database()

    elif args.action == "test":
        scripts.test(args.login, args.password)

    else:
        pass