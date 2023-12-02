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
            if db_handler.validate_email(
                login
            ):  # The case in which an e-mail was provided as Login
                db_handler.cursor.execute(
                    """
                    SELECT password
                    FROM users
                    WHERE email=?
                    """,
                    (login,),
                )
            elif db_handler.validate_phone_num(
                login
            ):  # The case in which a telephone number was provided as Login
                login = re.sub(r'\D', '', login)[-9:]

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
                print('\nInvalid Login\n')

        except TypeError:
            print('\nInvalid Login\n')

        except OperationalError:
            print(
                "\nThe database has not been created yet! Type 'python script.py create_database' to build it\n"
            )

    return wrapper


def check_if_admin(login):
    """Simple function to check if the given user has an admin role"""

    if '@' in login:
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

    if result == 'admin':
        return True
    return False


class Scripts:
    def __init__(self):
        pass

    def create_database(self):
        db_handler.create_database()
        print('\nDatabase has been successfully created and populated\n')

    """ADMIN ONLY METHODS"""

    @authenticate
    def print_all_accounts(self, login, password) -> int:
        """Return the total number of valid accounts"""

        if check_if_admin(login):
            db_handler.cursor.execute(
                """
                SELECT COUNT(1) FROM users
                """
            )
            result = db_handler.cursor.fetchone()[0]
            print(int(result))
        else:
            print('\nInvalid Login - admin role required\n')

    @authenticate
    def print_oldest_account(self, login, password) -> str:
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
                f'name: {result[1]}\nemail_address: {result[3]}\ncreated_at: {result[6]}'
            )

        else:
            print('\nInvalid Login - admin role required\n')

    @authenticate
    def group_by_age(self, login, password) -> str:
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
                for age in re.findall(r'\d+', row[0]):
                    children_age.append(int(age))

            c = Counter(children_age)
            sorted_age = dict(sorted(c.items(), key=lambda x: x[1]))
            # Sort age of the children by count- ascending

            for key, value in sorted_age.items():
                print(f'age: {key}, count: {value}')

        else:
            print('\nInvalid Login - admin role required\n')

    """BOTH ADMIN AND USER METHODS"""

    @authenticate
    def print_children(self, login, password) -> str:
        """Return personal data of the logged-in user's children, sorted by name"""

        if '@' in login:
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

        result = db_handler.cursor.fetchone()

        if result[0] != '[]':
            children_data = json.loads(result[0])  # Extract the children data

            sorted_children = sorted(children_data, key=lambda x: x.get('name', ''))

            for child in sorted_children:
                print(f"{child['name']}, {child['age']}")
        else:
            print('\nThis user has no children\n')

    @authenticate
    def find_similar_children_by_age(self, login, password) -> str:
        """Find users with children of the same age as at least user's one own child"""

        user_children_age = []
        common_users = []  # Avoid duplicating the output list of rows
        common_phone_numbers = []  # --||--

        if '@' in login:
            db_handler.cursor.execute(
                """
                SELECT children, telephone_number
                FROM users
                WHERE email=?
                """,
                (login,),
            )
        else:
            db_handler.cursor.execute(
                """
                SELECT children, telephone_number
                FROM users
                WHERE telephone_number=?
                """,
                (login,),
            )

        c = db_handler.cursor.fetchone()
        result = json.loads(c[0])
        
        # Get the phone number of the logged in user to exclude their details from the output message
        login = c[1]
        
        if result == []: 
            print('\nThis user has no children\n')
            return
        
        for child in result:
            user_children_age.append(child['age'])  # Get the age of user's each child

        db_handler.cursor.execute(
            """
            SELECT firstname, telephone_number, children
            FROM users
            """
        )
        result = db_handler.cursor.fetchall()

        # Extracting children data of subsequent users row by row
        for user in result:
            children_data = json.loads(user[2])
            user_phone_number = user[1]

            for child in children_data:
                if child['age'] in user_children_age:   
                    """Check whether any of the children of the checked user 
                    are the same age as the child of the logged in user"""
                    if user_phone_number not in common_phone_numbers and user_phone_number != login:
                        common_users.append(
                            {
                                'firstname': user[0],
                                'phone_number': user_phone_number,
                                'children': children_data,
                            }
                        )
                        common_phone_numbers.append(user_phone_number)
                        
        for user in common_users:
            
            children = sorted(
                user['children'], key=lambda x: x.get('name', '')
            )  # Sort children alphabetically by names
            response = f"{user['firstname']}, {user['phone_number']}: "

            for child in children:
                response += f"{child['name']}, {child['age']}; "

            print(response[:-2])


if __name__ == '__main__':
    db_handler = DataHandler('dbsqlite3')
    parser = argparse.ArgumentParser()
    scripts = Scripts()

    parser.add_argument(
        'action',
        choices=[
            'create_database',
            'print-all-accounts',
            'print-oldest-account',
            'group-by-age',
            'print-children',
            'find-similar-children-by-age',
        ],
    )
    parser.add_argument('--login', help='Login information', const=0, nargs='?')
    parser.add_argument('--password', help='Password information', const=0, nargs='?')

    args = parser.parse_args()

    if (args.action == 'create_database'):
        scripts.create_database()

    elif args.action == 'print-all-accounts':
        scripts.print_all_accounts(args.login, args.password)

    elif args.action == 'print-oldest-account':
        scripts.print_oldest_account(args.login, args.password)

    elif args.action == 'group-by-age':
        scripts.group_by_age(args.login, args.password)

    elif args.action == 'print-children':
        scripts.print_children(args.login, args.password)

    elif args.action == 'find-similar-children-by-age':
        scripts.find_similar_children_by_age(args.login, args.password)
