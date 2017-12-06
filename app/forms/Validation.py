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
        print(data)
        valid = 1
        data = json.loads(json.dumps(data))
        email = check_email(data["email"])
        print(email)
        valid *= len(email) > 0
        valid *= len(data['username']) > 3 and len(data['username']) < 25
        valid *= len(data['firstName']) > 1 and len(data['firstName']) < 25
        valid *= len(data['lastName']) > 1 and len(data['lastName']) < 25
        valid *= len(data['password']) > 6
        valid *= data['password'] == data['confirmPassword']
        print(valid)
        if valid:
            print('Valid')
            data['email'] = email
            return data
        else:
            return None
    except Exception as e:
        return None