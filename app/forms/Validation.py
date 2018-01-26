import json
from email_validator import validate_email, EmailNotValidError


def check_email(email):
    try:
        v = validate_email(email)
        email = v["email"]
        return email
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        print(str(e))

    return ''


def register_user(data):
    try:
        valid = 1
        data = json.loads(json.dumps(data))
        email = check_email(data.get("email"))
        valid *= len(email) > 0
        valid *= len(data.get('username', '')
                     ) > 3 and len(data.get('username', '')) < 26
        valid *= len(data.get('first_name', '')) < 26
        valid *= len(data.get('last_name', '')) < 35
        valid *= len(data.get('password', '')) > 5
        valid *= data.get('password', '') == data.get('confirmPassword', 'x')
        if valid:
            print('Valid')
            data['email'] = email
            return data
        else:
            print('Not Valid')
            return None
    except Exception as e:
        print('Error', e)
        return None


def edit_user(data):
    valid = 1
    data = json.loads(json.dumps(data))

    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    confirmPassword = data.get('confirmPassword')
    password = data.get('password')
    oldPassword = data.get('oldPassword')

    valid *= len(username) > 3 and len(username) < 26
    valid *= not first_name or len(first_name) < 26
    valid *= not last_name or len(last_name) < 26
    valid *= check_email(email)
    valid *= (not password and not confirmPassword) or (
        confirmPassword == password and len(password) > 6)
    valid *= len(oldPassword) > 6

    return data if valid else None


import json
from email_validator import validate_email, EmailNotValidError


def check_email(email):
    try:
        v = validate_email(email)
        email = v["email"]
        return email
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        print(str(e))

    return ''


def register_user(data):
    try:
        valid = 1
        data = json.loads(json.dumps(data))
        email = check_email(data.get("email"))
        valid *= len(email) > 0
        valid *= len(data.get('username', '')
                     ) > 3 and len(data.get('username', '')) < 26
        valid *= len(data.get('first_name', '')) < 26
        valid *= len(data.get('last_name', '')) < 35
        valid *= len(data.get('password', '')) > 5
        valid *= data.get('password', '') == data.get('confirmPassword', 'x')
        if valid:
            print('Valid')
            data['email'] = email
            return data
        else:
            print('Not Valid')
            return None
    except Exception as e:
        print('Error', e)
        return None


def edit_user(data):
    valid = 1
    data = json.loads(json.dumps(data))

    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    confirmPassword = data.get('confirmPassword')
    password = data.get('password')
    oldPassword = data.get('oldPassword')

    valid *= len(username) > 3 and len(username) < 26
    # print(valid)
    valid *= not first_name or len(first_name) < 26
    # print(valid)
    valid *= not last_name or len(last_name) < 26
    # print(valid)
    valid *= len(check_email(email)) > 0
    # print(valid)
    valid *= (not password and not confirmPassword) or (
        confirmPassword == password and len(password) > 6)
    # print(valid)
    valid *= len(oldPassword) >= 6
    # print(valid)

    return data if valid else None
