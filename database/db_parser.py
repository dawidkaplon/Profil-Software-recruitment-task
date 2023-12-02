import json
import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path

manager_directory = Path(__file__).resolve().parent


class DataParser:
    """Class to parse the data from the given .xml, .csv and .json data files"""

    def __init__(self):
        pass

    @classmethod
    def convert_to_common_format(cls, data, source_format):
        """Convert data so everything has the same format"""

        common_data = []

        if source_format in ('json', 'xml', 'csv'):
            for user in data:
                common_item = {
                    'firstname': user['firstname'],
                    'telephone_number': user['telephone_number'],
                    'email': user['email'],
                    'password': user['password'],
                    'role': user['role'],
                    'created_at': user['created_at'],
                    'children': user.get('children', []),
                }
                common_data.append(common_item)

        return common_data

    @classmethod
    def parse_json(cls, filename):
        # Absolute path to the data file
        path = manager_directory / 'data' / filename

        with open(path, 'r') as f:
            json_data = json.load(f)

            return json_data

    @classmethod
    def parse_xml(cls, filename):
        path1 = manager_directory / 'data' / f'{filename}1.xml'
        path2 = manager_directory / 'data' / f'{filename}2.xml'

        xml_data1 = []
        xml_data2 = []

        tree1 = ET.parse(path1)
        root1 = tree1.getroot()

        tree2 = ET.parse(path2)
        root2 = tree2.getroot()

        roots_to_use = [root1, root2]
        data_containers = [xml_data1, xml_data2]

        for i in range(2):
            for user in roots_to_use[i].findall('user'):
                user_data = {}
                user_data['firstname'] = user.find('firstname').text
                user_data['telephone_number'] = user.find('telephone_number').text
                user_data['email'] = user.find('email').text
                user_data['password'] = user.find('password').text
                user_data['role'] = user.find('role').text
                user_data['created_at'] = user.find('created_at').text

                if (
                    user.findall('.//child') == []
                ):  # Set children list empty when no child was found
                    user_data['children'] = []
                else:
                    for child in user.findall('.//child'):
                        child_data = {}
                        child_data['name'] = child.findtext('name')
                        child_data['age'] = child.findtext('age')
                        user_data['children'] = user_data.get('children', []) + [
                            child_data
                        ]
                data_containers[i].append(user_data)

        return xml_data1, xml_data2

    @classmethod
    def parse_csv(cls, filename):
        path1 = manager_directory / 'data' / f'{filename}1.csv'
        path2 = manager_directory / 'data' / f'{filename}2.csv'

        csv_data1 = []
        csv_data2 = []

        name_regex = re.compile('[A-Za-z]*')
        age_regex = re.compile('\d+')

        # Parse 1st csv file
        with open(path1, 'r') as csv1:
            reader1 = csv.DictReader(csv1, delimiter=';')
            for row in reader1:
                children_data = []
                row['children'] = cls.parse_children(row.get('children', ''))
                for child in row[
                    'children'
                ]:  # Make children data to appear as same as data in .xml, .json files
                    children_data.append(
                        {
                            'name': ''.join(re.findall(name_regex, child)),
                            'age': ''.join(re.findall(age_regex, child)),
                        }
                    )
                row['children'] = children_data

                csv_data1.append(row)

        # Parse 2nd csv file
        with open(path2, 'r') as csv2:
            reader2 = csv.DictReader(csv2, delimiter=';')
            for row in reader2:
                children_data = []
                row['children'] = cls.parse_children(row.get('children', ''))
                for child in row['children']:
                    children_data.append(
                        {
                            'name': ''.join(re.findall(name_regex, child)),
                            'age': ''.join(re.findall(age_regex, child)),
                        }
                    )
                row['children'] = children_data

                csv_data2.append(row)

        return csv_data1, csv_data2

    @classmethod
    def parse_children(cls, children_string):
        # Split the comma-separated string into a list of individual children data
        return [child.strip() for child in children_string.split(',') if child.strip()]
