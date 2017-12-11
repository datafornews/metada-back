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
                     ) > 3 and len(data.get('username', '')) < 25
        valid *= len(data.get('first_name', '')) < 25
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
