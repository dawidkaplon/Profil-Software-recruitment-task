# PROFIL SOFTWARE Recruitment task - Dawid Kapłon

## Description

These instructions will help You set up and run the project on Your local machine.

### Prerequisites

- Python installed

<p></p>

### Installation

***1. Clone the repo:***
```sh
git clone https://github.com/dawidkaplon/Profil-Software-recruitment-task.git
```

<br>

***2. Navigate to your project directory and then create virtual environment & activate it***
```sh
cd path/to/project
```

<br>

• If you're on Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

<br>

• If you're on Linux/MacOS:
```sh
python -m venv venv
source venv/bin/activate
```

<br>

***3. Install dependencies:***
```sh
pip install -r requirements.txt
```

<br>

## Navigating the project

<br>

- **You must be in the same directory as the script.py file to start typing commands**
- **The Login is either the user's e-mail address or his phone number**
<br>
<br>

🚨 **Note: Before working on the database, it's essential to create new one by typing the following command:**
```sh
python script.py create_database
```
• You should then see a successful output message and it will all be Yours from then on

<br><br>

🚨 **Note: If You are a Linux user, You may encounter the following syntax errors:**
```sh
bash: syntax error near unexpected token `(' ' :
```
<br>

• The best way to avoid these is to simply put Your login and password in single quotes:
```sh
python script.py <command> --login 'login' --password 'password'
```

<br>

### Available commands

- **Get total number of valid accounts (admin only)**
```sh
python script.py print-all-accounts --login <login> --password <password>
```

<br>

- **Get information about the longest existing account in the database (admin only)**
```sh
python script.py print-oldest-account --login <login> --password <password>
```

<br>

- **Show children data grouped by age, sorted ascending (admin only)**
```sh
python script.py group-by-age --login <login> --password <password>
```

<br>

- **Show details of the current user's children**
```sh
python script.py print-children --login <login> --password <password>
```

<br>

- **Find users with children of the same age as at least one own child, print the user and all of his children data. Sort children alphabetically by name**
```sh
python script.py find-similar-children-by-age --login <login> --password <password>
```

<br>

## Running tests

**•  While in the script.py directory, simply enter the following command:**
```sh
python -m pytest tests/tests.py
```

<br>
